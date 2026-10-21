package runs

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/samplingpreset"
)

// Client-side coalescing for RWKV bench runs: what bench sweep passes to
// agent-eval and what run check expects in harness.remote_batch_wait_ms and
// harness.remote_batch_max. rwkv_lightning has no cross-request batching, so
// unmerged calls are bsz=1 loops bound by memory bandwidth. Runs from before
// 2026-10-15 used 0 (no coalescing); they still pass, but a batched and an
// unbatched run differ in batch shape (fp16 results can differ slightly), so
// they are not paired directly.
const (
	BenchRemoteBatchWait = rwkvlightning.DefaultBatchWait
	BenchRemoteBatchMax  = rwkvlightning.DefaultBatchMax
	// BenchRemoteBatchInflight matches the 3-card 8018 gateway plus one; pass
	// the endpoint's card count to sweep and check when it differs.
	BenchRemoteBatchInflight = rwkvlightning.DefaultBatchInflight
)

// Validity gate for one agent-eval run (docs/evaluations/benchmark-protocol.md
// §6). Prints PASS/FAIL per gate and a strict score, where invalid cases count
// as failures. Exit status is 1 when any gate fails.

// ArmField is one sampling field. The value keeps Python's int-vs-float
// spelling because the gate line prints it verbatim ("1" for greedy's integer
// temperature, "1.0" for backend's float).
type ArmField struct {
	Key   string
	Value any
}

type Arm struct {
	Fields []ArmField
}

func (a Arm) Get(key string) (any, bool) {
	for _, v := range a.Fields {
		if v.Key == key {
			return v.Value, true
		}
	}
	return nil, false
}

func newArm(pairs ...any) Arm {
	var values []ArmField
	for i := 0; i+1 < len(pairs); i += 2 {
		values = append(values, ArmField{pairs[i].(string), pairs[i+1]})
	}
	return Arm{Fields: values}
}

// Arms is check_run.py's ARMS table, copied item for item.
//
// The sweep grid keys are generated there as "t%02d-p%02d" % (round(t*10),
// round(p*10)) over t in (0.3, 0.6, 1.0) and p in (1.0, 0.5), which is where
// t03-p10, t03-p05, t06-p10, t06-p05, t10-p10 and t10-p05 come from.
var Arms = func() map[string]Arm {
	out := map[string]Arm{
		"greedy": newArm("temperature", 1, "top_k", 1, "top_p", 1,
			"presence_penalty", 0, "frequency_penalty", 0, "penalty_decay", 1),
		"t03": newArm("temperature", 0.3, "top_k", 65536, "top_p", 1,
			"presence_penalty", 0, "frequency_penalty", 0, "penalty_decay", 1),
		"backend": newArm("temperature", 1.0, "top_k", 20, "top_p", 0.3,
			"presence_penalty", 2.0, "frequency_penalty", 0.2, "penalty_decay", 0.996),
		"backend-nopen": newArm("temperature", 1.0, "top_k", 20, "top_p", 0.3,
			"presence_penalty", 0, "frequency_penalty", 0, "penalty_decay", 1),
	}
	for _, t := range []float64{0.3, 0.6, 1.0} {
		for _, p := range []float64{1.0, 0.5} {
			key := fmt.Sprintf("t%02d-p%02d", int(t*10+0.5), int(p*10+0.5))
			out[key] = newArm("temperature", t, "top_k", 65536, "top_p", p,
				"presence_penalty", 0, "frequency_penalty", 0, "penalty_decay", 1)
		}
	}
	out["t03-p05-pr05"] = newArm("temperature", 0.3, "top_k", 65536, "top_p", 0.5,
		"presence_penalty", 0.5, "frequency_penalty", 0.1, "penalty_decay", 0.996)
	out["t03-p05-pr10"] = newArm("temperature", 0.3, "top_k", 65536, "top_p", 0.5,
		"presence_penalty", 1.0, "frequency_penalty", 0.1, "penalty_decay", 0.996)

	// Named presets (internal/samplingpreset, `rwkv-cli --sampling <name>`).
	// Keep in step with the Go table; TestPresetValuesArePinned guards that side.
	out[samplingpreset.AgentDefault] = out["t03-p05"]
	out[samplingpreset.AgentFast] = out["t03-p05-pr05"]
	out[samplingpreset.AgentStable] = out["backend-nopen"]
	// The retired spellings stay selectable: a sweep command written before
	// 2026-10-21 says g1k-agent. The preset gate canonicalises both sides, so
	// either spelling matches either a new or an old run.json.
	out["g1k-agent"] = out["t03-p05"]
	out["g1k-agent-fast"] = out["t03-p05-pr05"]
	out["g1k-stable"] = out["backend-nopen"]
	return out
}()

// apiUnsupported are the fields API providers drop; they are not part of the
// arm there.
var apiUnsupported = map[string]bool{"top_k": true, "penalty_decay": true}

// ArmNames lists the arms, sorted, the way argparse's choices would.
func ArmNames() []string {
	names := make([]string, 0, len(Arms))
	for name := range Arms {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// CheckArgs are the `run check` flags.
type CheckArgs struct {
	RunDir             string
	Arm                string
	RWKV               bool
	Primitive          bool
	Cases              int
	HasCases           bool
	MaxSteps           int
	MaxTokens          int
	DecisionMaxTokens  int
	CaseTimeoutSeconds int
	// Profile is the --profile the run must have used. Empty means the
	// agent-wire-v1.0 preset; anything else (format ablations such as
	// agent-wire-v1.0+think-fast) is matched against harness.wire_profile
	// verbatim.
	Profile string
	// RemoteBatchWaitMS and RemoteBatchMax are the expected RWKV coalescing
	// settings. A run recorded with no coalescing (0) also passes, with a
	// note that it does not pair with batched runs.
	RemoteBatchWaitMS int
	RemoteBatchMax    int
	// RemoteBatchInflight is the expected harness.remote_batch_inflight.
	RemoteBatchInflight int
}

// RunCheck is the `run check` command.
func RunCheck(args CheckArgs) int {
	return RunCheckTo(os.Stdout, args)
}

// RunCheckCaptured runs the gate and returns its report text and exit code,
// which the sweep records in each run's experiment.json.
func RunCheckCaptured(args CheckArgs) (string, int) {
	var buf strings.Builder
	code := RunCheckTo(&buf, args)
	return buf.String(), code
}

// RunCheckTo writes the gate report to w. gate() prints there too, so the
// captured and the on-line reports are the same bytes.
func RunCheckTo(w io.Writer, args CheckArgs) int {
	run, err := LoadJSONFile(args.RunDir+"/run.json", true)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	summary, err := LoadJSONFile(args.RunDir+"/summary.json", true)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	want, ok := Arms[args.Arm]
	if !ok {
		fmt.Fprintf(stderr, "error: unknown arm %q; choose from %s\n",
			args.Arm, strings.Join(ArmNames(), ", "))
		return 2
	}

	harness := lab.MapOf(run, "harness")
	model := lab.MapOf(run, "model")
	sampling := lab.MapOf(run, "sampling")
	var failures []string

	gate := func(name string, ok bool, detail string) {
		line := "FAIL " + name
		if ok {
			line = "PASS " + name
		}
		if detail != "" {
			line += "  (" + detail + ")"
		}
		fmt.Fprintln(w, line)
		if !ok {
			failures = append(failures, name)
		}
	}

	if args.RWKV && !args.Primitive {
		if args.Profile == "" || wire.CanonicalPresetName(args.Profile) == wire.AgentWireV1 {
			// run.json from before 2026-10-21 says g1k; both spellings name
			// the same wire, so a recorded alias passes the gate.
			recorded := wire.CanonicalPresetName(lab.StringOf(harness, "wire_preset"))
			gate("wire_preset is "+wire.AgentWireV1, recorded == wire.AgentWireV1,
				fmt.Sprintf("wire_preset=%s", pyRepr(harness["wire_preset"])))
		} else {
			gate("wire_profile == "+args.Profile, lab.StringOf(harness, "wire_profile") == args.Profile,
				fmt.Sprintf("wire_profile=%s", pyRepr(harness["wire_profile"])))
		}
	}
	if !args.RWKV {
		gate("completion == chat-completions", lab.StringOf(model, "completion") == "chat-completions",
			fmt.Sprintf("completion=%s", pyRepr(model["completion"])))
	}

	if _, isPreset := presetArms[args.Arm]; isPreset {
		if _, hasPreset := sampling["preset"]; hasPreset {
			// Binaries from 2026-09-23 on record the preset matched from the
			// values that ran. Old runs record the retired name, so compare
			// the current name of both sides.
			recorded := samplingpreset.CanonicalName(lab.StringOf(sampling, "preset"))
			want := samplingpreset.CanonicalName(args.Arm)
			gate(fmt.Sprintf("sampling.preset == %s", args.Arm), recorded == want,
				fmt.Sprintf("got %s", pyRepr(sampling["preset"])))
		}
	}

	for _, field := range want.Fields {
		if !args.RWKV && apiUnsupported[field.Key] {
			continue
		}
		got := sampling[field.Key]
		gate(fmt.Sprintf("sampling.%s == %s", field.Key, PyStr(field.Value)),
			closeEnough(got, field.Value),
			fmt.Sprintf("got %s", pyRepr(got)))
	}

	if args.Primitive {
		fmt.Fprintf(w, "SKIP max_steps / decision_max_output_tokens (suite-owned: %s / %s)\n",
			pyRepr(harness["max_steps"]), pyRepr(harness["decision_max_output_tokens"]))
	} else {
		gate(fmt.Sprintf("max_steps == %d", args.MaxSteps),
			intEquals(harness["max_steps"], args.MaxSteps),
			fmt.Sprintf("got %s", pyRepr(harness["max_steps"])))
	}
	gate(fmt.Sprintf("answer_max_output_tokens == %d", args.MaxTokens),
		intEquals(harness["answer_max_output_tokens"], args.MaxTokens),
		fmt.Sprintf("got %s", pyRepr(harness["answer_max_output_tokens"])))

	if !args.Primitive {
		gate(fmt.Sprintf("decision_max_output_tokens == %d", args.DecisionMaxTokens),
			intEquals(harness["decision_max_output_tokens"], args.DecisionMaxTokens),
			fmt.Sprintf("got %s", pyRepr(harness["decision_max_output_tokens"])))
	}

	gate(fmt.Sprintf("case_timeout_seconds == %d", args.CaseTimeoutSeconds),
		intEquals(harness["case_timeout_seconds"], args.CaseTimeoutSeconds),
		fmt.Sprintf("got %s (absent before 2026-09-23 binaries)", pyRepr(harness["case_timeout_seconds"])))
	if args.RWKV {
		checkRemoteBatch(gate, harness, args.RemoteBatchWaitMS, args.RemoteBatchMax, args.RemoteBatchInflight)
	}

	caseIDs := sliceOf(run, "case_ids")
	if args.HasCases {
		gate(fmt.Sprintf("case count == %d", args.Cases), len(caseIDs) == args.Cases,
			fmt.Sprintf("got %d", len(caseIDs)))
	}

	metrics := lab.MapOf(summary, "metrics")
	task := lab.MapOf(metrics, "task_success")
	invalid, _ := lab.IntOf(metrics["invalid_cases"])
	correct, _ := lab.IntOf(task["correct"])
	strictTotal := len(caseIDs)
	if strictTotal == 0 {
		strictTotal, _ = lab.IntOf(task["total"])
	}

	fmt.Println()
	fmt.Printf("model      %s  (%s)\n", PyStr(model["identifier"]), PyStr(model["completion"]))
	fmt.Printf("official   %d/%s  (invalid excluded from denominator)\n", correct, PyStr(task["total"]))
	if strictTotal != 0 {
		fmt.Printf("strict     %d/%d = %.1f%%  (invalid counted as failures)\n",
			correct, strictTotal, 100*float64(correct)/float64(strictTotal))
	} else {
		fmt.Println("strict     n/a")
	}
	fmt.Printf("invalid    %d  — transport errors must be re-run and merged before scoring\n", invalid)
	if len(failures) > 0 {
		fmt.Printf("\nINVALID RUN: %d gate(s) failed\n", len(failures))
		return 1
	}
	fmt.Println("\nrun passes the validity gate")
	return 0
}

// presetArms are the arms that are also named presets, and so are expected to
// be echoed in sampling.preset. The retired spellings are included: an old
// sweep command still selects them, and its run may record either name.
var presetArms = map[string]bool{
	"greedy": true, "backend": true,
	samplingpreset.AgentDefault: true, samplingpreset.AgentFast: true, samplingpreset.AgentStable: true,
	"g1k-agent": true, "g1k-agent-fast": true, "g1k-stable": true,
}

func closeEnough(got, want any) bool {
	if got == nil {
		return false
	}
	g, gok := lab.NumberValue(got)
	w, wok := lab.NumberValue(want)
	if !gok || !wok {
		return false
	}
	diff := g - w
	if diff < 0 {
		diff = -diff
	}
	return diff < 1e-4
}

// checkRemoteBatch gates the client-side coalescing settings. The expected
// window passes, and so does 0: runs from before coalescing became the bench
// default recorded 0 and stay valid on their own, but are flagged as not
// pairable with batched runs.
func checkRemoteBatch(gate func(string, bool, string), harness map[string]any, wantWaitMS, wantMax, wantInflight int) {
	gotWait := harness["remote_batch_wait_ms"]
	gotMax, _ := lab.IntOf(harness["remote_batch_max"]) // absent before 2026-10-15
	if wantWaitMS == 0 || !intEquals(gotWait, 0) {
		gate(fmt.Sprintf("remote_batch_wait_ms == %d", wantWaitMS), intEquals(gotWait, wantWaitMS),
			fmt.Sprintf("got %s", pyRepr(gotWait)))
		if wantWaitMS != 0 && intEquals(gotWait, wantWaitMS) {
			gate(fmt.Sprintf("remote_batch_max == %d", wantMax), gotMax == wantMax,
				fmt.Sprintf("got %d", gotMax))
			gotInflight, _ := lab.IntOf(harness["remote_batch_inflight"])
			gate(fmt.Sprintf("remote_batch_inflight == %d", wantInflight), gotInflight == wantInflight,
				fmt.Sprintf("got %d", gotInflight))
		}
		return
	}
	gate(fmt.Sprintf("remote_batch_wait_ms == %d (or 0, unbatched)", wantWaitMS), true,
		"got 0: unbatched run; batch settings differ from the current protocol, do not pair it directly with batched runs")
}

func intEquals(got any, want int) bool {
	i, ok := lab.IntOf(got)
	return ok && i == want
}

// PyStr is Python's str() for the arm values, which are ints or floats.
func PyStr(v any) string {
	switch t := v.(type) {
	case int:
		return fmt.Sprintf("%d", t)
	case float64:
		return pyFloatString(t)
	case string:
		return t
	}
	return fmt.Sprintf("%v", v)
}

// pyRepr is Python's repr() for the values a gate detail quotes.
func pyRepr(v any) string {
	switch t := v.(type) {
	case nil:
		return "None"
	case bool:
		if t {
			return "True"
		}
		return "False"
	case string:
		return lab.PyRepr(t)
	case json.Number:
		if strings.ContainsAny(t.String(), ".eE") {
			if f, err := t.Float64(); err == nil {
				return pyFloatString(f)
			}
		}
		return t.String()
	case float64:
		return pyFloatString(t)
	case int:
		return fmt.Sprintf("%d", t)
	}
	return fmt.Sprintf("%v", v)
}

func pyFloatString(f float64) string {
	return labPyFloat(f)
}
