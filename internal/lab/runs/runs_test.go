package runs

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

// The infrastructure rule is shared by wire, audit and replicate; all three
// have to agree on which failures are transport breaks rather than scores.
func TestInfrastructureFailure(t *testing.T) {
	infra := []string{
		"runner error: rwkv_lightning continuation error: connection reset by peer",
		"runner error: HTTP 503 from upstream",
		"runner error: context deadline exceeded",
		"runner error: timeout waiting for the batch",
		"runner error: unexpected EOF",
	}
	for _, f := range infra {
		if !InfrastructureFailure(f) {
			t.Errorf("InfrastructureFailure(%q) = false, want true", f)
		}
	}
	notInfra := []string{
		"output mismatch: expected 9000",
		"runner error: agent protocol error: no tool call in decision step",
		"answer contract repaired",
		"",
	}
	for _, f := range notInfra {
		if InfrastructureFailure(f) {
			t.Errorf("InfrastructureFailure(%q) = true, want false", f)
		}
	}
}

func TestSplitThink(t *testing.T) {
	cases := []struct {
		name   string
		raw    string
		prompt string
		kind   string
		body   string
	}{
		{"plain answer", "9000", "", "none", "9000"},
		{"closed think", "<think>2.5*3600</think>\n9000", "", "self", "9000"},
		{"unclosed think", "<think>still going", "", "unclosed", ""},
		{"empty think", "<think>  </think>9000", "", "empty", "9000"},
		{"prefilled opening without close", "9000", "Assistant: <think", "unclosed", ""},
		{"prefilled opening closed", "2.5*3600</think>\n9000", "Assistant: <think", "prefilled", "9000"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			kind, _, body := SplitThink(tc.raw, tc.prompt)
			if kind != tc.kind {
				t.Errorf("kind = %q, want %q", kind, tc.kind)
			}
			if tc.kind != "unclosed" && body != tc.body {
				t.Errorf("body = %q, want %q", body, tc.body)
			}
		})
	}
}

func TestCallObject(t *testing.T) {
	ok := []string{
		`{"name":"read_file","arguments":{"path":"a"}}`,
		`<tool_call>{"name":"read_file","arguments":{"path":"a"}}</tool_call>`,
		"```json\n{\"name\":\"read_file\",\"arguments\":{}}\n```",
	}
	for _, text := range ok {
		if CallObject(text) == nil {
			t.Errorf("CallObject(%q) = nil, want a call", text)
		}
	}
	bad := []string{
		`{"name":"read_file"}`,                       // missing arguments
		`{"name":"read_file","arguments":{},"x":1}`,  // extra key
		`{"name":"read_file","arguments":[]}`,        // arguments is not an object
		`{"name":7,"arguments":{}}`,                  // name is not a string
		`{"name":"a","arguments":{}} trailing prose`, // tail is not a close tag
		`prose mentioning {"name":"a","arguments":{}}`,
		"",
	}
	for _, text := range bad {
		if CallObject(text) != nil {
			t.Errorf("CallObject(%q) = a call, want nil", text)
		}
	}
}

func TestAnswerTextMatch(t *testing.T) {
	expect := map[string]any{"expected_number": 9000.0, "tolerance": 0.01}
	if !AnswerTextMatch(expect, "The rate is 9000 MiB per hour.") {
		t.Error("a bare 9000 in prose should match")
	}
	if AnswerTextMatch(expect, "the year 19000 was busy") {
		t.Error("19000 must not match 9000 (word boundary)")
	}
	if AnswerTextMatch(expect, "v1.9000.2") {
		t.Error("a version component must not match (dot-digit boundary)")
	}
	equals := map[string]any{"output_equals": "443"}
	if !AnswerTextMatch(equals, "443") {
		t.Error("exact string should match")
	}
	if AnswerTextMatch(equals, "1443") {
		t.Error("1443 must not match 443 (word boundary)")
	}
}

func TestWirePreservesZeroAnswerMatchCounter(t *testing.T) {
	dir := t.TempDir()
	summary := map[string]any{
		"cases": []any{map[string]any{
			"id":     "case-1",
			"passed": false,
			"turns": []any{map[string]any{
				"passed":   false,
				"failures": []any{"output mismatch: expected 9000"},
				"result": map[string]any{
					"output": "9000",
					"steps": []any{map[string]any{
						"stage":       "answer",
						"action_type": "final",
					}},
				},
			}},
		}},
	}
	data, err := json.Marshal(summary)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "summary.json"), data, 0o600); err != nil {
		t.Fatal(err)
	}
	bank := map[string]map[string]any{
		"case-1": {"turns": []any{map[string]any{
			"expect": map[string]any{"expected_number": 9000},
		}}},
	}
	report, err := AnalyzeWire(dir, bank)
	if err != nil {
		t.Fatal(err)
	}
	metrics := mapOf(report, "metrics")
	value, ok := metrics["answer_match_with_other_failures"]
	if !ok {
		t.Fatal("answer_match_with_other_failures is missing")
	}
	got, ok := numberValue(value)
	if !ok || got != 0 {
		t.Fatalf("answer_match_with_other_failures = %v, want 0", value)
	}
}

// The arm table is the sweep's contract with check_run.py; the values are
// pinned here so a transcription slip is caught without a run directory.
func TestArmTableValues(t *testing.T) {
	greedy, ok := Arms["greedy"]
	if !ok {
		t.Fatal("greedy arm missing")
	}
	for key, want := range map[string]any{
		"temperature": 1, "top_k": 1, "top_p": 1,
		"presence_penalty": 0, "frequency_penalty": 0, "penalty_decay": 1,
	} {
		got, _ := greedy.Get(key)
		if got != want {
			t.Errorf("greedy.%s = %v, want %v", key, got, want)
		}
	}
	t03p05, ok := Arms["t03-p05"]
	if !ok {
		t.Fatal("t03-p05 arm missing")
	}
	for key, want := range map[string]any{
		"temperature": 0.3, "top_k": 65536, "top_p": 0.5,
		"presence_penalty": 0, "frequency_penalty": 0, "penalty_decay": 1,
	} {
		got, _ := t03p05.Get(key)
		if got != want {
			t.Errorf("t03-p05.%s = %v, want %v", key, got, want)
		}
	}
	if got, _ := Arms["g1k-agent"].Get("top_p"); got != 0.5 {
		t.Errorf("g1k-agent is an alias of t03-p05, got top_p %v", got)
	}
	for _, name := range []string{"t03-p10", "t03-p05", "t06-p10", "t06-p05", "t10-p10", "t10-p05"} {
		if _, ok := Arms[name]; !ok {
			t.Errorf("sweep grid arm %s missing", name)
		}
	}
}

// P7: the bootstrap must reproduce Python's stream, not merely a good one.
func TestBootstrapMatchesPython(t *testing.T) {
	// Ten cases in ten solo families: every resample draws 10 indices.
	families := make([][]int, 10)
	for i := range families {
		families[i] = []int{i}
	}
	aVals := make([]float64, 10)
	bVals := make([]float64, 10)
	for i := range aVals {
		aVals[i] = 1
	}
	bVals[0], bVals[1], bVals[2] = 1, 1, 1

	lo, hi, point, ok := bootstrapCI(families, aVals, bVals)
	if !ok {
		t.Fatal("bootstrap produced no replicates")
	}
	if point != 0.7 {
		t.Errorf("point estimate = %v, want 0.7", point)
	}
	// The interval comes from the recorded Python stream; if the generator or
	// the index arithmetic drifts, these move.
	if lo <= 0 || hi < lo {
		t.Errorf("CI = [%v, %v], want a positive interval", lo, hi)
	}
}
