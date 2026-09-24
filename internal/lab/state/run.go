package state

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

// Run a state evaluation with serial before/after fingerprints and file
// identity. Uses the raw continuation endpoint, never chat template defaults.
// Fingerprints are drift guards, not cryptographic proof of server-side loaded
// tensor bytes.
//
// This command also absorbs what scripts/wire-experiment.py did: §2.5 deletes
// that script, and the suite runs it launched are the whole point of the
// driver, so the command it built is constructed here instead of shelled out.

const (
	// DefaultRoot holds upload receipts, canaries and suite outputs.
	DefaultRoot = "runs/state-check-20260919"
	// WireProfile is the wire the state evaluations run under.
	WireProfile = "xml-v1+align-qwen36+no-tool+bare+one-stage"
	// WireModel is the model every state request names.
	WireModel = "rwkv-g1k-7b-temp-3601"
	// DefaultAPIURL is the endpoint; RWKV_LAB_API_URL overrides it, which is
	// what the fake-server verification points at.
	DefaultAPIURL = "https://api-7b.rwkvos.com/v1"
)

// APIURL is the endpoint base, overridable for offline verification.
func APIURL() string {
	if override := os.Getenv("RWKV_LAB_API_URL"); override != "" {
		return strings.TrimRight(override, "/")
	}
	return DefaultAPIURL
}

func digest(data []byte) string {
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:])
}

// effectiveFingerprint applies the existing client text stops to both raw
// canaries, which is the diagnostic distinction the driver records.
func effectiveFingerprint(record map[string]any) string {
	var outputs []string
	for _, row := range mapSlice(record["requests"]) {
		text := stringOf(row, "output")
		cut := -1
		for _, stop := range []string{"</tool_call>", "\nUser:", "\nSystem:", "\nTool:"} {
			if idx := strings.Index(text, stop); idx != -1 && (cut == -1 || idx < cut) {
				cut = idx
			}
		}
		if cut >= 0 {
			text = text[:cut]
		}
		outputs = append(outputs, text)
	}
	data, err := lab.EncodeJSON(outputs, 0)
	if err != nil {
		return digest(nil)
	}
	return digest(data)
}

func httpRequest(headers map[string]string, path string, body *lab.OrderedMap) (map[string]any, error) {
	// urllib sends a GET when there is no body, which state/list relies on.
	method := "GET"
	var reader io.Reader
	if body != nil {
		method = "POST"
		// Python's json.dumps(body, ensure_ascii=False) uses the default
		// ", " / ": " separators, and the recorded request bytes are compared
		// against the original's.
		data, err := lab.EncodeOrderedJSON(body, lab.EncodeOptions{SpacedSeparators: true})
		if err != nil {
			return nil, err
		}
		reader = strings.NewReader(string(data))
	}
	request, err := http.NewRequest(method, APIURL()+"/"+path, reader)
	if err != nil {
		return nil, err
	}
	for key, value := range headers {
		request.Header.Set(key, value)
	}
	// Match urllib's transport defaults so the recorded requests compare equal:
	// Go would otherwise ask for gzip and keep the connection alive.
	request.Header.Set("Accept-Encoding", "identity")
	request.Close = true
	client := &http.Client{Timeout: 180 * time.Second}
	response, err := client.Do(request)
	if err != nil {
		return nil, err
	}
	defer response.Body.Close()
	data, err := io.ReadAll(response.Body)
	if err != nil {
		return nil, err
	}
	obj, err := lab.DecodeOrderedJSON(data)
	if err != nil {
		return nil, err
	}
	m, ok := obj.(*lab.OrderedMap)
	if !ok {
		return nil, fmt.Errorf("%s: response is not a JSON object", path)
	}
	return m.AsMap(), nil
}

// canaryFingerprint sends the two synthetic canary tasks and records what came
// back. No benchmark answer is injected; these requests never execute
// generated tools or receive scores.
func canaryFingerprint(headers map[string]string, stateID string, fast bool, destination string) (map[string]any, error) {
	trainingPath := "datasets/data/normalized/v1-selection-baseline/rwkv-agent-state-v1-none-ctx4096.jsonl"
	trainingLine, err := firstLine(trainingPath)
	if err != nil {
		return nil, err
	}
	text, _ := trainingLine["text"].(string)
	system := text
	if idx := strings.Index(text, "<tools>"); idx != -1 {
		system = text[:idx]
	}
	catalog := []any{
		orderedOf("name", "read_file", "description",
			"Read one UTF-8 text file inside the workspace, up to 64 KiB.",
			"arguments", orderedOf("path", "relative file path")),
		orderedOf("name", "no_tool", "description",
			"Indicate that none of the offered tools is needed. Put a brief, complete user-facing response in reason; it becomes the final reply.",
			"arguments", orderedOf("reason", "brief complete user-facing response")),
	}
	var parts []string
	for _, item := range catalog {
		data, err := lab.EncodeOrderedJSON(item, lab.EncodeOptions{})
		if err != nil {
			return nil, err
		}
		parts = append(parts, string(data))
	}
	system += "<tools>[\n" + strings.Join(parts, ",\n") + "\n]</tools>"

	tasks := []string{
		"Read settings/canary.txt and report its verification word. Do not guess the file contents.",
		"Hello! No file inspection is needed. Please greet me briefly.",
	}
	stateList, err := httpRequest(headers, "state/list", nil)
	if err != nil {
		return nil, err
	}
	record := lab.NewOrderedMap()
	record.Set("state_id", stateID)
	record.Set("fast", fast)
	record.Set("started_unix", float64(time.Now().UnixNano())/1e9)
	record.Set("state_list", stateList)
	record.Set("requests", []any{})

	var requestRows []any
	for _, task := range tasks {
		prompt := system + "\n\nUser: " + task + "\n\nAssistant:"
		if fast {
			prompt += " <think></think"
		}
		body := lab.NewOrderedMap()
		body.Set("model", WireModel)
		body.Set("contents", []any{prompt})
		body.Set("max_tokens", 128)
		body.Set("temperature", 1)
		body.Set("top_k", 1)
		body.Set("top_p", 1)
		body.Set("alpha_presence", 0)
		body.Set("alpha_frequency", 0)
		body.Set("alpha_decay", 1)
		body.Set("stop_tokens", []any{0})
		body.Set("stream", false)
		body.Set("chunk_size", 1)
		if stateID != "" {
			body.Set("state_id", stateID)
		}
		response, err := httpRequest(headers, "batch/completions", body)
		if err != nil {
			return nil, err
		}
		output := firstChoiceContent(response)

		sortedBody, _ := lab.EncodeOrderedJSON(body,
			lab.EncodeOptions{SortKeys: true, SpacedSeparators: true})
		row := lab.NewOrderedMap()
		row.Set("request", body)
		row.Set("request_sha256", digest(sortedBody))
		row.Set("output", output)
		row.Set("output_sha256", digest([]byte(output)))
		row.Set("response", response)
		requestRows = append(requestRows, row)
		record.Set("requests", requestRows)
		if err := writeIndented(destination, record); err != nil {
			return nil, err
		}
	}
	var outputHashes []string
	for _, row := range requestRows {
		m, _ := row.(*lab.OrderedMap)
		outputHashes = append(outputHashes, stringOf(m.AsMap(), "output_sha256"))
	}
	hashData, _ := lab.EncodeOrderedJSON(outputHashes, lab.EncodeOptions{SpacedSeparators: true})
	record.Set("fingerprint", digest(hashData))
	if err := writeIndented(destination, record); err != nil {
		return nil, err
	}
	return record.AsMap(), nil
}

func orderedOf(pairs ...any) *lab.OrderedMap {
	m := lab.NewOrderedMap()
	for i := 0; i+1 < len(pairs); i += 2 {
		m.Set(pairs[i].(string), pairs[i+1])
	}
	return m
}

func firstChoiceContent(response map[string]any) string {
	choices, _ := response["choices"].([]any)
	if len(choices) == 0 {
		return ""
	}
	choice, _ := choices[0].(map[string]any)
	message, _ := choice["message"].(map[string]any)
	content, _ := message["content"].(string)
	return content
}

func firstLine(path string) (map[string]any, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	data, err := io.ReadAll(file)
	if err != nil {
		return nil, err
	}
	for _, line := range lab.SplitLines(string(data)) {
		if strings.TrimSpace(line) == "" {
			continue
		}
		obj, err := lab.DecodeJSONBytes([]byte(line))
		if err != nil {
			return nil, err
		}
		m, _ := obj.(map[string]any)
		return m, nil
	}
	return nil, fmt.Errorf("%s has no rows", path)
}

func writeIndented(path string, v any) error {
	data, err := lab.EncodeOrderedJSON(v, lab.EncodeOptions{Indent: 2})
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(data, '\n'), 0o644)
}

// RunArgs are the `state run` flags.
type RunArgs struct {
	Name             string
	StateID          string
	Fast             bool
	LegacyHistory    bool
	Wire             string
	AllowCanaryDrift bool
	Suites           string
	Parallelism      int
	Credentials      string
	Root             string
}

// RunState is the `state run` command.
func RunState(args RunArgs) int {
	root := args.Root
	if err := os.MkdirAll(root, 0o755); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	cred, err := runs.LoadJSONFile(args.Credentials, true)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	headers := map[string]string{
		"CF-Access-Client-Id":     stringOf(cred, "WIRE_CF_ID"),
		"CF-Access-Client-Secret": stringOf(cred, "WIRE_CF_SECRET"),
		"User-Agent":              "curl/8.7.1",
		"Content-Type":            "application/json",
	}

	var upload map[string]any
	if args.StateID != "" {
		upload, err = runs.LoadJSONFile(filepath.Join(root, args.StateID+".upload.json"), true)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
		if upload != nil {
			localPath := stringOf(upload, "local_path")
			data, err := os.ReadFile(localPath)
			if err != nil || digest(data) != stringOf(upload, "sha256") {
				fmt.Fprintln(os.Stderr, "state upload receipt does not match the local file")
				return 1
			}
		}
	}

	for _, suite := range strings.Split(args.Suites, ",") {
		parallelism := args.Parallelism
		if parallelism == 0 {
			parallelism = map[string]int{"workbank": 40, "boundary": 18, "bfcl": 60}[suite]
		}
		name := args.Name + "-" + suite
		dest := filepath.Join(root, name)
		before := filepath.Join(root, name+".canary-before.json")
		after := filepath.Join(root, name+".canary-after.json")
		if exists(dest) || exists(before) {
			fmt.Fprintf(os.Stderr, "Refusing overwrite %s\n", name)
			return 1
		}
		fmt.Println("CANARY BEFORE", name)
		a, err := canaryFingerprint(headers, args.StateID, args.Fast, before)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
		registered := registeredStates(a, args.StateID)
		if args.StateID != "" {
			size, _ := intOf(upload["size_bytes"])
			if len(registered) != 1 || intOfAny(registered[0]["size_bytes"]) != size {
				fmt.Fprintln(os.Stderr, "State registration absent or mismatched")
				return 1
			}
		}

		code, err := runWireExperiment(args, suite, name, root, parallelism)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}

		fmt.Println("CANARY AFTER", name)
		b, err := canaryFingerprint(headers, args.StateID, args.Fast, after)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
		stable := stringOf(a, "fingerprint") == stringOf(b, "fingerprint")
		effectiveStable := effectiveFingerprint(a) == effectiveFingerprint(b)
		current := registeredStates(b, args.StateID)
		stableRegistration := sameRegistrations(registered, current)

		experimentPath := filepath.Join(dest, "experiment.json")
		if exists(experimentPath) {
			e, err := runs.LoadJSONFile(experimentPath, true)
			if err == nil && e != nil {
				om := toOrdered(e)
				om.Set("state_file", upload)
				om.Set("canary_before", before)
				om.Set("canary_after", after)
				om.Set("canary_stable", stable)
				om.Set("state_registration_stable", stableRegistration)
				om.Set("canary_effective_stable", effectiveStable)
				om.Set("canary_effective_note", "Applies existing client text stops to both raw canaries; "+
					"diagnostic distinction only. Strict raw fingerprint validity is retained.")
				valid, _ := e["valid_for_model_comparison"].(bool)
				om.Set("transport_valid_for_model_comparison", valid)
				om.Set("valid_for_model_comparison", valid && stable && stableRegistration)
				om.Set("state_fingerprint_note", "run.json state_sha256 may hash ID string; "+
					"state_file.sha256 here hashes the actual local .pth bytes.")
				writeIndented(experimentPath, om)
			}
		}
		fmt.Println("VALIDITY", name, "canary_stable", pyBool(stable), "registration_stable", pyBool(stableRegistration))

		if args.AllowCanaryDrift && !stable && effectiveStable {
			if exists(experimentPath) {
				if e, err := runs.LoadJSONFile(experimentPath, true); err == nil && e != nil {
					om := toOrdered(e)
					om.Set("canary_drift_tolerated", true)
					transport, _ := e["transport_valid_for_model_comparison"].(bool)
					om.Set("valid_for_model_comparison", transport && stableRegistration)
					writeIndented(experimentPath, om)
				}
			}
			fmt.Println("CANARY DRIFT TOLERATED", name, "effective_stable", pyBool(effectiveStable))
			continue
		}
		if code != 0 || !stable || !stableRegistration {
			fmt.Fprintln(os.Stderr, "Run excluded; inspect transport/canary before continuing")
			return 1
		}
	}
	return 0
}

func toOrdered(m map[string]any) *lab.OrderedMap {
	// Key order is not recoverable from a map; this only feeds a file whose
	// consumer reads fields by name.
	out := lab.NewOrderedMap()
	keys := make([]string, 0, len(m))
	for key := range m {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	for _, key := range keys {
		out.Set(key, m[key])
	}
	return out
}

func registeredStates(record map[string]any, stateID string) []map[string]any {
	list, _ := record["state_list"].(map[string]any)
	var out []map[string]any
	for _, item := range mapSlice(list["data"]) {
		if stringOf(item, "state_id") == stateID {
			out = append(out, item)
		}
	}
	return out
}

func sameRegistrations(a, b []map[string]any) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		av, _ := lab.EncodeJSON(a[i], 0)
		bv, _ := lab.EncodeJSON(b[i], 0)
		if string(av) != string(bv) {
			return false
		}
	}
	return true
}

// runWireExperiment builds and runs the agent-eval command that
// scripts/wire-experiment.py used to launch.
func runWireExperiment(args RunArgs, suite, name, root string, parallelism int) (int, error) {
	repo := lab.RepoRoot()
	binary := filepath.Join(repo, "build", "rwkv-cli-state-experiment")
	profile := WireProfile
	if args.Fast {
		profile += "+think-fast"
	}
	cmd := []string{binary, "agent-eval", "--completion", "rwkv-lightning-cuda",
		"--api-url", APIURL(),
		"--api-header-env", "CF-Access-Client-Id=WIRE_CF_ID",
		"--api-header-env", "CF-Access-Client-Secret=WIRE_CF_SECRET",
		"--api-header-env", "User-Agent=WIRE_UA",
		"--model", WireModel,
		"--profile", profile,
		"--temperature", "1", "--top-k", "1",
		"--max-steps", "10", "--case-parallelism", strconv.Itoa(parallelism),
		"--case-timeout", "30m",
		"--duplicate-rescue-threshold", "0", "--same-tool-rescue-limit", "0"}
	if args.StateID != "" {
		cmd = append(cmd, "--state-id", args.StateID)
	}
	if args.Wire != "" {
		cmd = append(cmd, "--wire", args.Wire)
	}
	cmd = append(cmd, "--api-stop-tokens", "eos", "--max-tokens", "1024")
	// state-experiment always asks for buffered responses.
	cmd = append(cmd, "--api-stream=false")
	switch suite {
	case "workbank":
		cmd = append(cmd, "--cases", "bench/workbank/cases", "--tool-catalog", "work-v1", "--file-tools", "lines")
	case "boundary":
		cmd = append(cmd, "--suite", "boundary")
	case "bfcl":
		cmd = append(cmd, "--suite", "bfcl-product")
	}
	output := filepath.Join(root, name)
	cmd = append(cmd, "--output", output)

	env := os.Environ()
	cred, err := runs.LoadJSONFile(args.Credentials, true)
	if err == nil {
		for key, value := range cred {
			if s, ok := value.(string); ok {
				env = append(env, key+"="+s)
			}
		}
	}
	env = append(env, "WIRE_UA=curl/8.7.1")

	started := time.Now()
	logPath := filepath.Join(root, name+".log")
	logFile, err := os.Create(logPath)
	if err != nil {
		return 0, err
	}
	fmt.Println("START", name, started.Format("2006-01-02 15:04:05"))
	proc := exec.Command(cmd[0], cmd[1:]...)
	proc.Dir = repo
	proc.Env = env
	proc.Stdout = logFile
	proc.Stderr = logFile
	runErr := proc.Run()
	logFile.Close()
	code := 0
	if proc.ProcessState != nil {
		code = proc.ProcessState.ExitCode()
	}
	_ = runErr

	summaryPath := filepath.Join(output, "summary.json")
	if !exists(summaryPath) {
		data, _ := os.ReadFile(logPath)
		if len(data) > 2000 {
			data = data[len(data)-2000:]
		}
		fmt.Fprintln(os.Stderr, string(data))
		return code, fmt.Errorf("No summary; stopping matrix")
	}
	summary, err := runs.LoadJSONFile(summaryPath, true)
	if err != nil {
		return code, err
	}

	provenance := lab.NewOrderedMap()
	provenance.Set("command", toAnySlice(cmd))
	binaryData, err := os.ReadFile(binary)
	if err == nil {
		provenance.Set("binary_sha256", digest(binaryData))
	}
	provenance.Set("git_head", gitOutput("rev-parse", "HEAD"))
	provenance.Set("diff_sha256", digest([]byte(gitOutput("diff", "HEAD"))))
	provenance.Set("started_unix", float64(started.UnixNano())/1e9)
	provenance.Set("evaluation_scope", "original_suite")
	provenance.Set("state_id", args.StateID)
	if suite == "workbank" {
		root := filepath.Join(repo, "bench", "workbank", "cases")
		provenance.Set("case_source", root)
		provenance.Set("case_source_sha256", caseSourceSHA256(root))
	}

	budgets := map[string]int{}
	var errors []string
	for _, c := range mapSlice(summary["cases"]) {
		for _, t := range mapSlice(c["turns"]) {
			for _, st := range mapSlice(mapOf(t, "result")["steps"]) {
				budget := 0
				if request, ok := st["request"].(map[string]any); ok {
					budget, _ = intOf(request["max_output_tokens"])
				}
				budgets[strconv.Itoa(budget)]++
			}
			for _, f := range stringList(t["failures"]) {
				if runs.InfrastructureFailure(f) {
					errors = append(errors, f)
				}
			}
		}
	}
	budgetMap := lab.NewOrderedMap()
	budgetKeys := make([]string, 0, len(budgets))
	for key := range budgets {
		budgetKeys = append(budgetKeys, key)
	}
	sort.Strings(budgetKeys)
	for _, key := range budgetKeys {
		budgetMap.Set(key, budgets[key])
	}
	provenance.Set("actual_request_token_budgets", budgetMap)
	provenance.Set("valid_for_model_comparison", len(errors) == 0)
	provenance.Set("infrastructure_errors", toAnySlice(errors))
	provenance.Set("exit_code", code)
	provenance.Set("elapsed_seconds", time.Since(started).Seconds())
	writeIndented(filepath.Join(output, "experiment.json"), provenance)

	fmt.Printf("DONE %s %s seconds %d infra_errors %d\n", name, taskSuccessRepr(summaryPath),
		int(time.Since(started).Seconds()), len(errors))
	if len(errors) > 0 {
		return code, fmt.Errorf("Infrastructure error: run excluded, matrix stopped")
	}
	return code, nil
}

func gitOutput(args ...string) string {
	cmd := exec.Command("git", args...)
	cmd.Dir = lab.RepoRoot()
	out, err := cmd.Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
}

func caseSourceSHA256(root string) string {
	digestHash := sha256.New()
	var paths []string
	filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return nil
		}
		if !d.IsDir() && d.Name() == "case.json" {
			paths = append(paths, path)
		}
		return nil
	})
	sort.Strings(paths)
	for _, path := range paths {
		rel, err := filepath.Rel(root, path)
		if err != nil {
			continue
		}
		digestHash.Write([]byte(rel))
		digestHash.Write([]byte{0})
		data, err := os.ReadFile(path)
		if err == nil {
			digestHash.Write(data)
		}
	}
	return hex.EncodeToString(digestHash.Sum(nil))
}

func exists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

func toAnySlice(items []string) []any {
	out := make([]any, len(items))
	for i, item := range items {
		out[i] = item
	}
	return out
}

func stringOf(m map[string]any, key string) string {
	s, _ := m[key].(string)
	return s
}

func mapSlice(v any) []map[string]any {
	items, _ := v.([]any)
	out := make([]map[string]any, 0, len(items))
	for _, item := range items {
		if m, ok := item.(map[string]any); ok {
			out = append(out, m)
		}
	}
	return out
}

func stringList(v any) []string {
	items, _ := v.([]any)
	out := make([]string, 0, len(items))
	for _, item := range items {
		if s, ok := item.(string); ok {
			out = append(out, s)
		}
	}
	return out
}

// taskSuccessRepr is Python's repr of summary.metrics.task_success, which is
// what the DONE line prints. The key order comes from the file, so it is read
// with the order-preserving decoder rather than from the plain map.
func taskSuccessRepr(summaryPath string) string {
	obj, err := lab.DecodeOrderedJSONFile(summaryPath)
	if err != nil {
		return "{}"
	}
	root, _ := obj.(*lab.OrderedMap)
	if root == nil {
		return "{}"
	}
	metrics, _ := mapValue(root, "metrics").(*lab.OrderedMap)
	if metrics == nil {
		return "{}"
	}
	task, _ := mapValue(metrics, "task_success").(*lab.OrderedMap)
	if task == nil {
		return "{}"
	}
	parts := make([]string, 0, len(task.Keys))
	for _, key := range task.Keys {
		parts = append(parts, fmt.Sprintf("'%s': %s", key, pyValue(task.Values[key])))
	}
	return "{" + strings.Join(parts, ", ") + "}"
}

func mapValue(m *lab.OrderedMap, key string) any {
	if m == nil {
		return nil
	}
	v, _ := m.Get(key)
	return v
}

func pyValue(v any) string {
	switch t := v.(type) {
	case string:
		return "'" + t + "'"
	case bool:
		if t {
			return "True"
		}
		return "False"
	case nil:
		return "None"
	default:
		if i, ok := intOf(v); ok {
			return strconv.Itoa(i)
		}
		if f, ok := v.(float64); ok {
			return strconv.FormatFloat(f, 'g', -1, 64)
		}
		return fmt.Sprintf("%v", v)
	}
}

// pyBool is Python's str() for a bool.
func pyBool(b bool) string {
	if b {
		return "True"
	}
	return "False"
}

func mapOf(m map[string]any, key string) map[string]any {
	out, _ := m[key].(map[string]any)
	return out
}

func mapOfAny(m map[string]any, keys ...string) map[string]any {
	current := m
	for _, key := range keys {
		next, _ := current[key].(map[string]any)
		if next == nil {
			return nil
		}
		current = next
	}
	return current
}

func intOf(v any) (int, bool) {
	switch t := v.(type) {
	case json.Number:
		i, err := t.Int64()
		if err != nil {
			return 0, false
		}
		return int(i), true
	case int:
		return t, true
	case float64:
		return int(t), true
	}
	return 0, false
}

func intOfAny(v any) int {
	i, _ := intOf(v)
	return i
}
