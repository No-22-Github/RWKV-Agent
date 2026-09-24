package corpus

import (
	"path/filepath"
	"reflect"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/lab/similarity"
)

// Ported one for one from scripts/corpus/tests/test_corpus.py (§6 M1: all 14
// tests move over).

// om builds an OrderedMap from alternating keys and values.
func om(pairs ...any) *lab.OrderedMap {
	m := lab.NewOrderedMap()
	for i := 0; i+1 < len(pairs); i += 2 {
		m.Set(pairs[i].(string), pairs[i+1])
	}
	return m
}

// jsonCase parses a case literal, so tests can write records the way the data
// files spell them.
func jsonCase(t *testing.T, text string) *lab.OrderedMap {
	t.Helper()
	obj, err := lab.DecodeOrderedJSON([]byte(text))
	if err != nil {
		t.Fatal(err)
	}
	m, ok := obj.(*lab.OrderedMap)
	if !ok {
		t.Fatal("not an object")
	}
	return m
}

// --- test steps -------------------------------------------------------------

func step(action string, fields map[string]any) map[string]any {
	out := map[string]any{"stage": "decision", "action_type": action}
	for key, value := range fields {
		out[key] = value
	}
	return out
}

func toolStep(name string, arguments any) map[string]any {
	return step("tool", map[string]any{
		"tool":           name,
		"tool_arguments": arguments,
		"tool_executed":  true,
	})
}

func finalStep(text string) map[string]any {
	return step("final", map[string]any{"model_output": text})
}

// caseRun builds a CaseRun the way the Python helper does: the case's answer
// defaults to the last step's model_output.
func caseRun(t *testing.T, steps []map[string]any, output *string, passed bool, retries int) CaseRun {
	t.Helper()
	answer := ""
	if output != nil {
		answer = *output
	} else if len(steps) > 0 {
		if s, ok := steps[len(steps)-1]["model_output"].(string); ok {
			answer = s
		}
	}
	result := agent.Result{Output: answer}
	for _, s := range steps {
		result.Steps = append(result.Steps, toAgentStep(t, s))
	}
	return CaseRun{CaseID: "c", Passed: passed, Turns: []agent.Result{result}, Retries: retries}
}

func toAgentStep(t *testing.T, fields map[string]any) agent.Step {
	t.Helper()
	var step agent.Step
	if stage, ok := fields["stage"].(string); ok {
		step.Stage = agent.GenerationStage(stage)
	}
	if action, ok := fields["action_type"].(string); ok {
		step.ActionType = action
	}
	if name, ok := fields["tool"].(string); ok {
		step.Tool = name
	}
	if executed, ok := fields["tool_executed"].(bool); ok {
		step.ToolExecuted = executed
	}
	if text, ok := fields["model_output"].(string); ok {
		step.ModelOutput = text
	}
	if reason, ok := fields["tool_error"].(string); ok {
		step.ToolError = reason
	}
	if reason, ok := fields["tool_rejected_reason"].(string); ok {
		step.ToolRejected = reason
	}
	if arguments, ok := fields["tool_arguments"]; ok {
		data, err := lab.EncodeOrderedJSON(toOrdered(t, arguments), lab.EncodeOptions{})
		if err != nil {
			t.Fatal(err)
		}
		step.ToolArguments = data
	}
	return step
}

func toOrdered(t *testing.T, v any) any {
	t.Helper()
	switch value := v.(type) {
	case map[string]any:
		m := lab.NewOrderedMap()
		for key, item := range value {
			m.Set(key, toOrdered(t, item))
		}
		return m
	case []any:
		out := make([]any, len(value))
		for i, item := range value {
			out[i] = toOrdered(t, item)
		}
		return out
	default:
		return v
	}
}

// --- WireTest ---------------------------------------------------------------

func TestToolCallIsCompactNameFirstAndKeepsUnicode(t *testing.T) {
	got, err := ToolCall("read_file", om("path", "说明.md"))
	if err != nil {
		t.Fatal(err)
	}
	want := `<tool_call>{"name":"read_file","arguments":{"path":"说明.md"}}</tool_call>`
	if got != want {
		t.Errorf("ToolCall = %s, want %s", got, want)
	}
}

// --- ScriptTest -------------------------------------------------------------

func TestPathIDsRoundTrip(t *testing.T) {
	if got := BaseCaseID(PathID("cfg-0012", 2)); got != "cfg-0012" {
		t.Errorf("BaseCaseID(PathID(...)) = %s", got)
	}
	if got := BaseCaseID("cfg-0012"); got != "cfg-0012" {
		t.Errorf("BaseCaseID without a path suffix = %s", got)
	}
}

// --- PathsTest --------------------------------------------------------------

func TestNormalizeDropsDefaultsAndEmptyOptionalsOnly(t *testing.T) {
	got := NormalizeArguments("list_files", om("path", "", "max_depth", 3, "max_results", 20))
	if !reflect.DeepEqual(got.AsMap(), map[string]any{"max_results": 20}) {
		t.Errorf("normalize(list_files) = %v", got.AsMap())
	}
	// A float equal to an int default is not the default the harness applies.
	got = NormalizeArguments("list_files", om("max_depth", float64(3.0)))
	if !reflect.DeepEqual(got.AsMap(), map[string]any{"max_depth": float64(3.0)}) {
		t.Errorf("normalize(max_depth 3.0) = %v, want it kept", got.AsMap())
	}
	got = NormalizeArguments("read_lines", om("path", "a", "start_line", "", "end_line", 0))
	want := map[string]any{"path": "a", "end_line": 0}
	if !reflect.DeepEqual(got.AsMap(), want) {
		t.Errorf("normalize(read_lines) = %v, want %v", got.AsMap(), want)
	}
}

func TestExtractKeepsActionsInOrder(t *testing.T) {
	path, err := Extract(caseRun(t, []map[string]any{
		toolStep("list_files", map[string]any{"path": ""}),
		finalStep("42"),
	}, nil, true, 0))
	if err != nil {
		t.Fatal(err)
	}
	if len(path) != 2 || path[0].Tool != "list_files" || !path[1].Final {
		t.Fatalf("path = %+v", path)
	}
	want, _ := ToolCall("list_files", om())
	if path[0].Text != want {
		t.Errorf("tool action text = %s, want %s", path[0].Text, want)
	}
	if path[1].Text != "42" {
		t.Errorf("final action text = %q", path[1].Text)
	}
}

func TestExtractRejectsUncleanRuns(t *testing.T) {
	repaired := "y"
	cases := []struct {
		reason string
		run    CaseRun
	}{
		{"protocol retry", caseRun(t, []map[string]any{finalStep("x")}, nil, true, 1)},
		{"tool error or rejection", caseRun(t, []map[string]any{
			step("tool", map[string]any{
				"tool": "read_file", "tool_arguments": map[string]any{"path": "a"},
				"tool_executed": true, "tool_error": "missing",
			}),
			finalStep("x"),
		}, nil, true, 0)},
		{"answer repaired by the harness", caseRun(t, []map[string]any{finalStep("x")}, &repaired, true, 0)},
		{"answer stage (forced closeout)", caseRun(t, []map[string]any{
			step("final", map[string]any{"model_output": "x", "stage": "answer"}),
		}, nil, true, 0)},
		{"final before the last step", caseRun(t, []map[string]any{
			finalStep("x"),
			toolStep("read_file", map[string]any{"path": "a"}),
		}, ptr("x"), true, 0)},
	}
	for _, tc := range cases {
		t.Run(tc.reason, func(t *testing.T) {
			_, err := Extract(tc.run)
			if err == nil {
				t.Fatalf("expected Unclean %q", tc.reason)
			}
			if !strings.Contains(err.Error(), tc.reason) {
				t.Errorf("reason = %q, want it to contain %q", err.Error(), tc.reason)
			}
		})
	}
}

func TestSelectPrefersShortestThenNewToolSequences(t *testing.T) {
	readText, _ := ToolCall("read_file", om("path", "a"))
	searchText, _ := ToolCall("search_text", om("query", "a"))
	readBText, _ := ToolCall("read_file", om("path", "b"))
	read := Action{Text: readText, Tool: "read_file"}
	search := Action{Text: searchText, Tool: "search_text"}
	readB := Action{Text: readBText, Tool: "read_file"}
	answer := Action{Text: "42", Final: true}

	stat := &CaseStats{Drops: newOrderedCounter(), Candidates: []candidate{
		{Trajectory{search, read, answer}, 0},
		{Trajectory{read, answer}, 1},
		{Trajectory{read, answer}, 2},        // exact duplicate
		{Trajectory{readB, answer}, 3},       // same tool sequence as the kept (read, answer)
		{Trajectory{read, readB, answer}, 4}, // new shape but over the cap
	}}
	kept := Select(stat, 2)
	if len(kept) != 2 || !sameTrajectory(kept[0], Trajectory{read, answer}) ||
		!sameTrajectory(kept[1], Trajectory{search, read, answer}) {
		t.Errorf("kept = %+v", kept)
	}
	want := map[string]int{"duplicate path": 1, "same tool sequence": 1, "over per-case cap": 1}
	if !reflect.DeepEqual(stat.Drops.Counts, want) {
		t.Errorf("drops = %v, want %v", stat.Drops.Counts, want)
	}
}

func sameTrajectory(a, b Trajectory) bool {
	return trajectoryKey(a) == trajectoryKey(b)
}

func ptr(s string) *string { return &s }

// --- BankTest ---------------------------------------------------------------

const recordJSON = `{
  "id": "r1", "scenario": "cfg", "initial_files": {"a.txt": "7"},
  "expected": {"turn_expectation": {"output_contains": ["7"]}},
  "messages": [
    {"role": "user", "text": "What is in a.txt?"},
    {"role": "assistant", "kind": "tool_call", "name": "read_file",
     "arguments": {"path": "a.txt"}, "supervised": true},
    {"role": "tool", "payload": "{}"},
    {"role": "assistant", "kind": "final", "text": "7", "supervised": true}
  ]
}`

func TestRecordBecomesCaseAndScript(t *testing.T) {
	record := jsonCase(t, recordJSON)
	caseObj, err := RecordToCase(record)
	if err != nil {
		t.Fatal(err)
	}
	turns, _ := mapValue(caseObj, "turns").([]any)
	if len(turns) != 1 {
		t.Fatalf("turns = %v", turns)
	}
	turn, _ := turns[0].(*lab.OrderedMap)
	if mapString(turn, "prompt") != "What is in a.txt?" {
		t.Errorf("prompt = %q", mapString(turn, "prompt"))
	}
	expect, _ := mapValue(turn, "expect").(*lab.OrderedMap)
	contains, _ := mapValue(expect, "output_contains").([]any)
	if len(contains) != 1 || contains[0] != "7" {
		t.Errorf("expect = %v", expect.AsMap())
	}

	entry, err := RecordToScript(record)
	if err != nil {
		t.Fatal(err)
	}
	wantTool, _ := ToolCall("read_file", om("path", "a.txt"))
	if len(entry.Outputs) != 2 || entry.Outputs[0].Text != wantTool || entry.Outputs[1].Text != "7" {
		t.Errorf("outputs = %+v", entry.Outputs)
	}
}

func TestBankRoundTripAndDuplicateIDs(t *testing.T) {
	root := t.TempDir()
	writeCases := []*lab.OrderedMap{om("id", "b"), om("id", "a")}
	if err := Write(root, writeCases); err != nil {
		t.Fatal(err)
	}
	loaded, err := Load(root)
	if err != nil {
		t.Fatal(err)
	}
	var ids []string
	for _, c := range loaded {
		ids = append(ids, mapString(c, "id"))
	}
	if !reflect.DeepEqual(ids, []string{"a", "b"}) {
		t.Errorf("ids = %v, want [a b]", ids)
	}
	if _, err := ByID([]*lab.OrderedMap{om("id", "a"), om("id", "a")}); err == nil {
		t.Error("duplicate ids were accepted")
	}
}

func TestScriptPathsResolveToTheirBankCase(t *testing.T) {
	cases := map[string]*lab.OrderedMap{"c": om("id", "c", "files", om())}
	resolved, err := CasesForScript(cases, []*lab.OrderedMap{om("case_id", "c--p1"), om("case_id", "c--p2")})
	if err != nil {
		t.Fatal(err)
	}
	if len(resolved) != 2 || mapString(resolved[0], "id") != "c--p1" || mapString(resolved[1], "id") != "c--p2" {
		t.Errorf("resolved = %v", resolved)
	}
	if _, err := CasesForScript(cases, []*lab.OrderedMap{om("case_id", "d--p1")}); err == nil {
		t.Error("an unresolvable script id was accepted")
	}
}

// --- SimilarityTest ---------------------------------------------------------

func TestBoilerplateIsIgnored(t *testing.T) {
	template := "Reply with only the final answer and nothing else please."
	var population []similarity.Features
	for i := 0; i < 10; i++ {
		population = append(population, similarity.FeaturesOf(map[string]any{
			"turns": []any{map[string]any{"prompt": "task " + string(rune('0'+i)) + " " + template}},
		}))
	}
	common := similarity.Boilerplate(population, 0.05)
	if len(common.Prompt) == 0 {
		t.Fatal("no prompt features were treated as boilerplate")
	}
	candidate := similarity.Strip(similarity.FeaturesOf(map[string]any{
		"turns": []any{map[string]any{"prompt": "other " + template}},
	}), common)
	score := similarity.Scores(candidate, similarity.Strip(population[0], common))["prompt"]
	if score != 0.0 {
		t.Errorf("prompt score = %v, want 0 (the template is boilerplate)", score)
	}
}

func TestFixtureReuseCountsByContainment(t *testing.T) {
	fixture := map[string]any{"deploy.yaml": "a: 1\nb: 2\nc: 3\nd: 4\n"}
	test := similarity.FeaturesOf(map[string]any{"files": fixture})
	biggerFixture := map[string]any{"deploy.yaml": fixture["deploy.yaml"], "extra.txt": "x\ny\nz\nw\n"}
	bigger := similarity.FeaturesOf(map[string]any{"files": biggerFixture})
	if got := similarity.Scores(bigger, test)["files"]; got != 0.5 {
		t.Errorf("containment score = %v, want 0.5", got)
	}
	if got := similarity.Containment(test.Files, bigger.Files); got != 1.0 {
		t.Errorf("reverse containment = %v, want 1.0", got)
	}
}

func TestNearestFlagsARenamedCopy(t *testing.T) {
	original := map[string]any{
		"id":    "t1",
		"files": map[string]any{"svc/notify-hub.yaml": "retries: 3\ntimeout: 30\nregion: eu\n"},
		"turns": []any{map[string]any{"prompt": "How many retries does notify-hub allow before paging CHG-2193?"}},
	}
	unrelated := map[string]any{
		"id":    "t2",
		"files": map[string]any{"b.csv": "x,y\n1,2\n"},
		"turns": []any{map[string]any{"prompt": "Sum column y."}},
	}
	test := []testItem{
		{id: "t1", features: similarity.FeaturesOf(original)},
		{id: "t2", features: similarity.FeaturesOf(unrelated)},
	}
	common := similarity.Boilerplate([]similarity.Features{test[0].features, test[1].features}, 0.99)
	candidate := om("id", "cand")
	for _, key := range []string{"files", "turns"} {
		candidate.Set(key, toOrdered(t, original[key]))
	}
	row := nearest(candidate, test, common, map[string]float64{"prompt": 0.35, "files": 0.3, "names": 0.3})
	flagged := stringSlice(mapValue(row, "flagged"))
	if !reflect.DeepEqual(flagged, []string{"prompt", "files", "names"}) {
		t.Errorf("flagged = %v", flagged)
	}
	nearestMap, _ := mapValue(row, "nearest").(*lab.OrderedMap)
	if got := mapString(nearestMap, "files"); got != "t1" {
		t.Errorf("nearest files = %q, want t1", got)
	}
}

// --- CliTest ----------------------------------------------------------------

func TestRenderPassesFlagsAfterDoubleDashToAgentEval(t *testing.T) {
	var args RenderArgs
	fs := renderFlagSet(&args)
	if err := fs.Parse([]string{"--records", "r.jsonl", "--out", "o", "--", "--profile", "g1j"}); err != nil {
		t.Fatal(err)
	}
	args.Extra = fs.Args()
	if !reflect.DeepEqual(args.Extra, []string{"--profile", "g1j"}) {
		t.Errorf("extra = %v, want [--profile g1j]", args.Extra)
	}
}

func TestPathsAcceptsRepeatedRuns(t *testing.T) {
	var args PathsArgs
	var runs stringList
	fs := pathsFlagSet(&args, &runs)
	if err := fs.Parse([]string{"--run", "a", "--run", "b", "--out", "s.jsonl"}); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual([]string(runs), []string{"a", "b"}) {
		t.Errorf("runs = %v", runs)
	}
}

// P2: script.jsonl carries the teacher's raw action text, and <tool_call> is
// spelled with literal angle brackets. Go's encoding/json escapes them to
// < by default; if that crept back in, the script's bytes would no longer
// match the baseline and the training corpus would change spelling. The
// migration's negative test turns exactly this on and requires the comparison
// to fail.
func TestScriptJSONLKeepsAngleBracketsLiteral(t *testing.T) {
	path := filepath.Join(t.TempDir(), "script.jsonl")
	text := `<tool_call>{"name":"list_files","arguments":{}}</tool_call>`
	entry, err := ToolCall("list_files", om())
	if err != nil {
		t.Fatal(err)
	}
	if entry != text {
		t.Fatalf("ToolCall = %s, want %s", entry, text)
	}
	row := lab.NewOrderedMap()
	row.Set("case_id", "fs-0001")
	row.Set("outputs", []any{om("text", text, "supervised", true)})
	if err := WriteJSONL(path, []*lab.OrderedMap{row}, "x"); err != nil {
		t.Fatal(err)
	}
	written, err := lab.ReadText(path)
	if err != nil {
		t.Fatal(err)
	}
	for _, escaped := range []string{`\u003c`, `\u003e`, `\u0026`} {
		if strings.Contains(written, escaped) {
			t.Errorf("script.jsonl escaped HTML (%s present): %s", escaped, written)
		}
	}
	if !strings.Contains(written, "<tool_call>") {
		t.Errorf("script.jsonl lost the literal tool call: %s", written)
	}
}
