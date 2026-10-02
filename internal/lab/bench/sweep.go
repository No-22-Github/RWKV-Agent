// Package bench ports the sweep and rank tools: running a grid of sampling
// arms x suites x replicas against an RWKV endpoint, and ranking the arms that
// came back.
package bench

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/lab/runs"
)

// Suites maps a suite name to how it is invoked. name -> (short name for run
// directories, rwkv-cli suite args, case count, parallelism, uses g1k wire).
type suiteSpec struct {
	shortName   string
	args        []string
	count       int
	parallelism int
	g1k         bool
}

var suites = map[string]suiteSpec{
	"workbank": {"workbank", []string{"--cases", "bench/workbank/cases", "--tool-catalog", "work-v1",
		"--file-tools", "lines", "--include-draft"}, 148, 48, true},
	"bfcl-product":         {"bfclp", []string{"--suite", "bfcl-product"}, 60, 16, true},
	"boundary":             {"boundary", []string{"--suite", "boundary"}, 18, 18, true},
	"assistant":            {"assistant", []string{"--suite", "assistant"}, 6, 6, true},
	"smoke":                {"smoke", []string{"--suite", "smoke"}, 10, 10, true},
	"primitive-orig30":     {"porig30", []string{"--suite", "primitive-orig30"}, 30, 30, false},
	"primitive-feedback30": {"pfb30", []string{"--suite", "primitive-feedback30"}, 30, 30, false},
}

// parallelFor is the in-flight case cap passed to one suite's agent-eval. The
// spec value is the floor; the --max-concurrency budget scales it up when
// there is headroom (runArm packs suites into batches against the same cap).
func (args *SweepArgs) parallelFor(suite string) int {
	if n, ok := args.parallel[suite]; ok {
		return n
	}
	return suites[suite].parallelism
}

// scaledParallelism distributes budget across the selected suites
// proportionally to their spec parallelism, rounding up via largest
// remainders, so the sum lands exactly on budget. At or below the specs' sum
// every suite keeps its spec value and runArm batches sequentially instead.
func scaledParallelism(names []string, budget int) map[string]int {
	out := make(map[string]int, len(names))
	total := 0
	for _, name := range names {
		total += suites[name].parallelism
	}
	if budget <= total {
		for _, name := range names {
			out[name] = suites[name].parallelism
		}
		return out
	}
	type share struct {
		name       string
		base, frac int
	}
	shares := make([]share, 0, len(names))
	assigned := 0
	for _, name := range names {
		p := suites[name].parallelism
		exact := p * budget
		shares = append(shares, share{name, exact / total, exact % total})
		assigned += exact / total
	}
	sort.Slice(shares, func(i, j int) bool { return shares[i].frac > shares[j].frac })
	for i := range shares {
		if assigned < budget {
			shares[i].base++
			assigned++
		}
		out[shares[i].name] = shares[i].base
	}
	return out
}

func binaryPath() string { return filepath.Join(lab.RepoRoot(), "local", "bin", "rwkv-cli") }

// SweepArgs are the `bench sweep` flags.
type SweepArgs struct {
	Out            string
	Arms           []string
	Suites         []string
	K              string
	Model          string
	APIURL         string
	Prefix         string
	StateID        string
	Profile        string
	MaxConcurrency int
	MaxAttempts    int
	DryRun         bool
	bsz            int
	// parallel carries the per-suite in-flight case cap (scaledParallelism);
	// nil falls back to the suiteSpec values.
	parallel map[string]int
}

// profile is the wire profile of the g1k-wire suites: the g1k preset unless a
// format ablation passes --profile.
func (args *SweepArgs) profile() string {
	if args.Profile == "" {
		return "g1k"
	}
	return args.Profile
}

// RunSweep is the `bench sweep` command.
func RunSweep(args SweepArgs) int {
	replicas, err := parseK(args.K)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 2
	}
	for _, arm := range args.Arms {
		if _, ok := runs.Arms[arm]; !ok {
			fmt.Fprintf(os.Stderr, "unknown arm/suite: [%s]\n", arm)
			return 2
		}
	}
	for _, suite := range args.Suites {
		if _, ok := suites[suite]; !ok {
			fmt.Fprintf(os.Stderr, "unknown arm/suite: [%s]\n", suite)
			return 2
		}
	}

	// Dry run has no endpoint snapshot, so it shows the split the real run
	// would derive from the same budget (the snapshot can only lower it).
	args.parallel = scaledParallelism(args.Suites, args.MaxConcurrency)
	if args.DryRun {
		for _, k := range replicas {
			for _, arm := range args.Arms {
				for _, suite := range args.Suites {
					output := filepath.Join(args.Out, fmt.Sprintf("%s-%s-%s-k%d", args.Prefix, suites[suite].shortName, arm, k))
					prefix := "TODO  "
					if runDone(output) {
						prefix = "DONE  "
					}
					fmt.Println(prefix + strings.Join(sweepCommand(args, suite, arm, output), " "))
				}
			}
		}
		return 0
	}

	// Credentials come from the environment only, by name; they never reach a
	// file (P11).
	if os.Getenv("RWKV_CF_ID") == "" || os.Getenv("RWKV_CF_SECRET") == "" {
		fmt.Fprintln(os.Stderr, "RWKV_CF_ID and RWKV_CF_SECRET must be set")
		return 1
	}
	if _, err := os.Stat(binaryPath()); err != nil {
		fmt.Fprintf(os.Stderr, "missing %s; run: go build -o local/bin/rwkv-cli ./cmd/rwkv-cli\n", binaryPath())
		return 1
	}
	if err := os.MkdirAll(args.Out, 0o755); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	label := time.Now().Format("20060102-150405")
	ids, engine, bsz, err := snapshot(&args, "before-"+label)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	fmt.Printf("ENDPOINT %v %v hard_max_bsz=%v\n", ids, engine, bsz)
	found := false
	for _, id := range ids {
		if id == args.Model {
			found = true
		}
	}
	if !found {
		fmt.Fprintf(os.Stderr, "endpoint serves %v, not %s\n", ids, args.Model)
		return 1
	}
	limit := args.MaxConcurrency
	if bsz != nil {
		if n, ok := bsz.(int); ok && n < limit {
			limit = n
		}
	}
	args.bsz = limit
	args.parallel = scaledParallelism(args.Suites, limit)

	ok := true
	for _, k := range replicas {
		for _, arm := range args.Arms {
			current, err := endpointModels(args.APIURL)
			if err != nil {
				fmt.Fprintln(os.Stderr, err)
				return 1
			}
			if !sameStrings(current, ids) {
				fmt.Fprintf(os.Stderr, "endpoint model changed %v -> %v; stopping, this stage is void\n", ids, current)
				return 1
			}
			ok = runArm(&args, arm, k) && ok
		}
	}
	after, _, _, err := snapshot(&args, "after-"+label)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	if !sameStrings(after, ids) {
		fmt.Printf("ENDPOINT CHANGED %v -> %v: runs from this invocation are void\n", ids, after)
		return 1
	}
	if ok {
		fmt.Println("ALL DONE")
		return 0
	}
	fmt.Println("FINISHED WITH GIVE-UPS")
	return 1
}

func parseK(value string) ([]int, error) {
	if strings.Contains(value, "-") {
		parts := strings.SplitN(value, "-", 2)
		low, err1 := strconv.Atoi(parts[0])
		high, err2 := strconv.Atoi(parts[1])
		if err1 != nil || err2 != nil {
			return nil, fmt.Errorf("invalid --k %q", value)
		}
		var out []int
		for i := low; i <= high; i++ {
			out = append(out, i)
		}
		return out, nil
	}
	var out []int
	for _, part := range strings.Split(value, ",") {
		n, err := strconv.Atoi(part)
		if err != nil {
			return nil, fmt.Errorf("invalid --k %q", value)
		}
		out = append(out, n)
	}
	return out, nil
}

func armFlags(arm string) []string {
	values := runs.Arms[arm]
	var out []string
	for _, field := range []struct{ flag, key string }{
		{"--temperature", "temperature"}, {"--top-k", "top_k"}, {"--top-p", "top_p"},
		{"--presence-penalty", "presence_penalty"}, {"--frequency-penalty", "frequency_penalty"},
		{"--penalty-decay", "penalty_decay"},
	} {
		value, _ := values.Get(field.key)
		out = append(out, field.flag, runs.PyStr(value))
	}
	return out
}

func sweepCommand(args SweepArgs, suite, arm, output string) []string {
	spec := suites[suite]
	cmd := []string{binaryPath(), "agent-eval", "--completion", "rwkv-lightning-cuda",
		"--model", args.Model, "--api-url", args.APIURL,
		"--api-header-env", "CF-Access-Client-Id=RWKV_CF_ID",
		"--api-header-env", "CF-Access-Client-Secret=RWKV_CF_SECRET",
		"--max-steps", "16", "--max-tokens", "4096", "--case-parallelism", strconv.Itoa(args.parallelFor(suite)),
		// The CLI default is 2m; with ~150 cases sharing the backend a 16-step
		// case needs far longer, and the 2m clock cut 56/148 greedy cases on
		// 2026-09-23.
		"--case-timeout", "30m",
		// Without this the decision step falls back to the protocol default
		// (512). g1k thinks spontaneously on 142/148 first steps.
		"--decision-max-tokens", "2048",
		// Client-side coalescing hands every call its result only when the
		// whole merged response ends, so one looping member stalls the short
		// replies batched with it.
		"--remote-batch-wait", "0s"}
	if args.StateID != "" {
		cmd = append(cmd, "--state-id", args.StateID)
	}
	if spec.g1k {
		cmd = append(cmd, "--profile", args.profile(), "--strict-spec")
	}
	cmd = append(cmd, spec.args...)
	cmd = append(cmd, armFlags(arm)...)
	return append(cmd, "--output", output)
}

func runDone(path string) bool {
	meta, err := os.ReadFile(filepath.Join(path, "experiment.json"))
	if err != nil {
		return false
	}
	obj, err := lab.DecodeJSONBytes(meta)
	if err != nil {
		return false
	}
	m, _ := obj.(map[string]any)
	passed, _ := m["gate_passed"].(bool)
	return passed
}

func setAside(args *SweepArgs, path string) error {
	logPath := path + ".log"
	if !lab.Exists(path) && !lab.Exists(logPath) {
		return nil
	}
	aborted := filepath.Join(args.Out, "aborted")
	if err := os.MkdirAll(aborted, 0o755); err != nil {
		return err
	}
	stamp := time.Now().Format("20060102-150405")
	for _, source := range []string{path, logPath} {
		if lab.Exists(source) {
			if err := os.Rename(source, filepath.Join(aborted, filepath.Base(source)+"."+stamp)); err != nil {
				return err
			}
		}
	}
	return nil
}

func runArm(args *SweepArgs, arm string, k int) bool {
	type pendingRun struct {
		suite  string
		output string
	}
	var pending []pendingRun
	for _, suite := range args.Suites {
		output := filepath.Join(args.Out, fmt.Sprintf("%s-%s-%s-k%d", args.Prefix, suites[suite].shortName, arm, k))
		if runDone(output) {
			fmt.Printf("SKIP %s (done)\n", filepath.Base(output))
			continue
		}
		pending = append(pending, pendingRun{suite, output})
	}
	for attempt := 1; attempt <= args.MaxAttempts; attempt++ {
		if len(pending) == 0 {
			return true
		}
		var batches [][]pendingRun
		var current []pendingRun
		used := 0
		for _, item := range pending {
			need := args.parallelFor(item.suite)
			if len(current) > 0 && used+need > args.bsz {
				batches = append(batches, current)
				current, used = nil, 0
			}
			current = append(current, item)
			used += need
		}
		if len(current) > 0 {
			batches = append(batches, current)
		}
		var retry []pendingRun
		for _, batch := range batches {
			type running struct {
				suite   string
				output  string
				cmd     []string
				started time.Time
				proc    *exec.Cmd
				log     *os.File
			}
			var procs []running
			for _, item := range batch {
				if err := setAside(args, item.output); err != nil {
					fmt.Fprintln(os.Stderr, err)
					return false
				}
				cmd := sweepCommand(*args, item.suite, arm, item.output)
				fmt.Printf("START %s attempt %d  %s\n", filepath.Base(item.output), attempt, time.Now().Format("15:04:05"))
				logFile, err := os.Create(item.output + ".log")
				if err != nil {
					fmt.Fprintln(os.Stderr, err)
					return false
				}
				proc := exec.Command(cmd[0], cmd[1:]...)
				proc.Dir = lab.RepoRoot()
				proc.Stdout = logFile
				proc.Stderr = logFile
				if err := proc.Start(); err != nil {
					fmt.Fprintln(os.Stderr, err)
					logFile.Close()
					return false
				}
				procs = append(procs, running{item.suite, item.output, cmd, time.Now(), proc, logFile})
			}
			for _, p := range procs {
				_ = p.proc.Wait()
				p.log.Close()
				provenance, gateOK, line, err := finishRun(args, p.suite, arm, p.output, p.cmd, p.started)
				if err != nil {
					fmt.Fprintln(os.Stderr, err)
					return false
				}
				if !gateOK {
					// The run was configured wrongly; repeating it cannot help.
					fmt.Fprintf(os.Stderr, "GATE FAIL %s  %s\nfix the configuration; nothing marked done\n",
						filepath.Base(p.output), line)
					os.Exit(1)
				}
				errors := []any{"no summary"}
				if provenance != nil {
					errors = sliceOfAny(provenance, "infrastructure_errors")
				}
				final := attempt == args.MaxAttempts
				tag := "RETRY"
				if provenance != nil && (len(errors) == 0 || final) {
					// Last attempt: keep the run and count its invalid cases as
					// failures instead of retrying forever on a reproducible
					// break.
					provenance.Set("gate_passed", true)
					provenance.Set("accepted_with_infra_errors", len(errors) > 0)
					data, err := lab.EncodeOrderedJSON(provenance, lab.EncodeOptions{Indent: 2})
					if err == nil {
						os.WriteFile(filepath.Join(p.output, "experiment.json"), append(data, '\n'), 0o644)
					}
					if len(errors) == 0 {
						tag = "DONE"
					} else {
						tag = "KEEP"
					}
				} else {
					retry = append(retry, pendingRun{p.suite, p.output})
				}
				fmt.Printf("%s %s  %s\n", tag, filepath.Base(p.output), line)
			}
		}
		pending = retry
	}
	for _, item := range pending {
		fmt.Printf("GIVE-UP %s: no summary after %d attempts\n", filepath.Base(item.output), args.MaxAttempts)
	}
	return len(pending) == 0
}

// finishRun gates one finished run and builds its provenance record.
func finishRun(args *SweepArgs, suite, arm, output string, cmd []string, started time.Time) (*lab.OrderedMap, bool, string, error) {
	spec := suites[suite]
	summaryPath := filepath.Join(output, "summary.json")
	if !lab.Exists(summaryPath) {
		return nil, true, fmt.Sprintf("no summary.json; see %s.log", output), nil
	}
	summary, err := runs.LoadJSONFile(summaryPath, true)
	if err != nil {
		return nil, false, "", err
	}
	var errors []string
	for _, c := range lab.MapSlice(summary["cases"]) {
		for _, t := range lab.MapSlice(c["turns"]) {
			for _, f := range lab.StringList(t["failures"]) {
				if runs.InfrastructureFailure(f) {
					errors = append(errors, f)
				}
			}
		}
		if invalid, _ := c["invalid"].(bool); invalid {
			errors = append(errors, lab.StringOf(c, "invalid_reason"))
		}
	}

	// The gate runs in-process now; check_run.py is gone (M5).
	gateOut, gateCode := runs.RunCheckCaptured(runs.CheckArgs{
		RunDir:             output,
		Arm:                arm,
		RWKV:               true,
		Primitive:          !spec.g1k,
		Cases:              spec.count,
		HasCases:           true,
		MaxSteps:           16,
		MaxTokens:          4096,
		DecisionMaxTokens:  2048,
		CaseTimeoutSeconds: 1800,
		Profile:            args.profile(),
	})

	task := mapOfAny(summary, "metrics", "task_success")
	correct, _ := lab.IntOf(task["correct"])
	invalidCases, _ := lab.IntOf(mapOfAny(summary, "metrics")["invalid_cases"])

	binaryBytes, err := os.ReadFile(binaryPath())
	if err != nil {
		return nil, false, "", err
	}
	binarySum := sha256.Sum256(binaryBytes)
	gitHead := lab.GitOutput("rev-parse", "HEAD")
	gitDiff := lab.GitOutput("diff", "HEAD")
	diffSum := sha256.Sum256([]byte(gitDiff))

	provenance := lab.NewOrderedMap()
	provenance.Set("command", lab.ToAnySlice(cmd))
	provenance.Set("arm", arm)
	provenance.Set("suite", suite)
	provenance.Set("sampling", armSamplingMap(arm))
	provenance.Set("binary_sha256", hex.EncodeToString(binarySum[:]))
	provenance.Set("git_head", gitHead)
	provenance.Set("diff_sha256", hex.EncodeToString(diffSum[:]))
	provenance.Set("state_id", args.StateID)
	provenance.Set("profile", args.profile())
	provenance.Set("started_unix", float64(started.UnixNano())/1e9)
	provenance.Set("exit_code", lastExitCode)
	provenance.Set("elapsed_seconds", time.Since(started).Seconds())
	provenance.Set("infrastructure_errors", lab.ToAnySlice(errors))
	provenance.Set("valid_for_model_comparison", len(errors) == 0)
	provenance.Set("gate_output", gateOut)
	strict := lab.NewOrderedMap()
	strict.Set("correct", correct)
	strict.Set("total", len(lab.MapSlice(summary["cases"])))
	provenance.Set("strict", strict)
	if suite == "workbank" {
		root := filepath.Join(lab.RepoRoot(), "bench", "workbank", "cases")
		provenance.Set("case_source", root)
		provenance.Set("case_source_sha256", lab.CaseSourceSHA256(root))
	}

	line := fmt.Sprintf("strict %d/%d  invalid %d  infra_errors %d  gate %s  %.0fs",
		correct, len(lab.MapSlice(summary["cases"])), invalidCases, len(errors),
		map[bool]string{true: "PASS", false: "FAIL"}[gateCode == 0],
		time.Since(started).Seconds())
	if gateCode != 0 {
		for _, l := range lab.SplitLines(gateOut) {
			if strings.HasPrefix(l, "FAIL") {
				line += "\n" + l
			}
		}
	}
	return provenance, gateCode == 0, line, nil
}

// lastExitCode carries the child's exit status into provenance; the original
// recorded it from subprocess.Popen.wait().
var lastExitCode int

func armSamplingMap(arm string) map[string]any {
	values := runs.Arms[arm]
	out := map[string]any{}
	for _, key := range []string{"temperature", "top_k", "top_p", "presence_penalty", "frequency_penalty", "penalty_decay"} {
		value, _ := values.Get(key)
		out[key] = value
	}
	return out
}

// snapshot records the endpoint's model list and status before and after a
// sweep, so a mid-run model swap is visible in the artifacts.
func snapshot(args *SweepArgs, label string) ([]string, any, any, error) {
	models, err := endpointJSON(args.APIURL, "/models")
	if err != nil {
		return nil, nil, nil, err
	}
	status, err := endpointJSON(args.APIURL, "/server/status")
	if err != nil {
		return nil, nil, nil, err
	}
	writeIndented(filepath.Join(args.Out, "endpoint-"+label+"-models.json"), models)
	writeIndented(filepath.Join(args.Out, "endpoint-"+label+"-server-status.json"), status)
	var ids []string
	for _, m := range lab.MapSlice(models["data"]) {
		if id, ok := m["id"].(string); ok {
			ids = append(ids, id)
		}
	}
	queue := mapOfAny(status, "prefill_queue")
	return ids, status["engine_version"], queue["hard_max_bsz"], nil
}

func endpointModels(base string) ([]string, error) {
	models, err := endpointJSON(base, "/models")
	if err != nil {
		return nil, err
	}
	var ids []string
	for _, m := range lab.MapSlice(models["data"]) {
		if id, ok := m["id"].(string); ok {
			ids = append(ids, id)
		}
	}
	return ids, nil
}

func endpointJSON(base, path string) (map[string]any, error) {
	request, err := http.NewRequest("GET", strings.TrimRight(base, "/")+path, nil)
	if err != nil {
		return nil, err
	}
	request.Header.Set("CF-Access-Client-Id", os.Getenv("RWKV_CF_ID"))
	request.Header.Set("CF-Access-Client-Secret", os.Getenv("RWKV_CF_SECRET"))
	// Cloudflare answers python-urllib's default User-Agent with a bare 403.
	request.Header.Set("User-Agent", "curl/8.7.1")
	client := &http.Client{Timeout: 30 * time.Second}
	response, err := client.Do(request)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	body, err := io.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}
	obj, err := lab.DecodeJSONBytes(body)
	if err != nil {
		return nil, err
	}
	m, _ := obj.(map[string]any)
	return m, nil
}

func writeIndented(path string, v any) {
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		return
	}
	os.WriteFile(path, append(data, '\n'), 0o644)
}

func sameStrings(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}
