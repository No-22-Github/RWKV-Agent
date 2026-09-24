package runs

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"
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
}

// RunCheck is the `run check` command.
func RunCheck(args CheckArgs) int {
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

	harness := mapOf(run, "harness")
	model := mapOf(run, "model")
	sampling := mapOf(run, "sampling")
	var failures []string

	gate := func(name string, ok bool, detail string) {
		line := "FAIL " + name
		if ok {
			line = "PASS " + name
		}
		if detail != "" {
			line += "  (" + detail + ")"
		}
		fmt.Println(line)
		if !ok {
			failures = append(failures, name)
		}
	}

	if args.RWKV && !args.Primitive {
		gate("wire_preset == g1k", stringOf(harness, "wire_preset") == "g1k",
			fmt.Sprintf("wire_preset=%s", pyRepr(harness["wire_preset"])))
	}
	if !args.RWKV {
		gate("completion == chat-completions", stringOf(model, "completion") == "chat-completions",
			fmt.Sprintf("completion=%s", pyRepr(model["completion"])))
	}

	if _, isPreset := presetArms[args.Arm]; isPreset {
		if _, hasPreset := sampling["preset"]; hasPreset {
			// Binaries from 2026-09-23 on record the preset matched from the
			// values that ran.
			gate(fmt.Sprintf("sampling.preset == %s", args.Arm),
				stringOf(sampling, "preset") == args.Arm,
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
		fmt.Printf("SKIP max_steps / decision_max_output_tokens (suite-owned: %s / %s)\n",
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
		// A coalesced batch releases results only when its slowest member ends.
		gate("remote_batch_wait_ms == 0", intEquals(harness["remote_batch_wait_ms"], 0),
			fmt.Sprintf("got %s", pyRepr(harness["remote_batch_wait_ms"])))
	}

	caseIDs := sliceOf(run, "case_ids")
	if args.HasCases {
		gate(fmt.Sprintf("case count == %d", args.Cases), len(caseIDs) == args.Cases,
			fmt.Sprintf("got %d", len(caseIDs)))
	}

	metrics := mapOf(summary, "metrics")
	task := mapOf(metrics, "task_success")
	invalid, _ := intOf(metrics["invalid_cases"])
	correct, _ := intOf(task["correct"])
	strictTotal := len(caseIDs)
	if strictTotal == 0 {
		strictTotal, _ = intOf(task["total"])
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
// be echoed in sampling.preset.
var presetArms = map[string]bool{
	"greedy": true, "g1k-agent": true, "g1k-agent-fast": true,
	"g1k-stable": true, "backend": true,
}

func closeEnough(got, want any) bool {
	if got == nil {
		return false
	}
	g, gok := numberValue(got)
	w, wok := numberValue(want)
	if !gok || !wok {
		return false
	}
	diff := g - w
	if diff < 0 {
		diff = -diff
	}
	return diff < 1e-4
}

func intEquals(got any, want int) bool {
	i, ok := intOf(got)
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
		return pyQuote(t)
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
