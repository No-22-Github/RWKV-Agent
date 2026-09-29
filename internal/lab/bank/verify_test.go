package bank

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// testdata is the fixture set verify_all.py shipped with: two tabular cases
// that should pass, one of which carries a deliberately unparseable verify.py,
// and a web case using the {"expected": ...} output shape.
func TestVerifyTestdata(t *testing.T) {
	requirePython3(t)
	testdata := filepath.Join(lab.RepoRoot(), "bench", "workbank", "tools", "testdata")
	out, code := captureOutput(t, func() int {
		return runVerify([]string{"--cases", testdata})
	})
	if code != 1 {
		t.Errorf("exit code = %d, want 1 (tab-9002 is the failing fixture)", code)
	}
	var report struct {
		Total   int `json:"total"`
		Passed  int `json:"passed"`
		Failed  int `json:"failed"`
		Results []struct {
			Case   string `json:"case"`
			OK     bool   `json:"ok"`
			Checks []struct {
				Check string `json:"check"`
				OK    bool   `json:"ok"`
				Error string `json:"error"`
			} `json:"checks"`
		} `json:"results"`
	}
	if err := json.Unmarshal([]byte(out), &report); err != nil {
		t.Fatalf("report is not JSON: %v\n%s", err, out)
	}
	if report.Total != 3 || report.Passed != 2 || report.Failed != 1 {
		t.Errorf("total/passed/failed = %d/%d/%d, want 3/2/1", report.Total, report.Passed, report.Failed)
	}
	for _, result := range report.Results {
		if result.Case != "tab-9002" {
			if !result.OK {
				t.Errorf("case %s failed but should pass: %+v", result.Case, result.Checks)
			}
			continue
		}
		if result.OK {
			t.Error("tab-9002 passed but its verify.py is not valid Python")
		}
		if len(result.Checks) == 0 || result.Checks[0].Check != "verify_run" {
			t.Errorf("tab-9002 first check = %+v, want verify_run", result.Checks)
		}
	}
}

// P9: the sandbox conditions are what stop a case's LLM-drafted verify.py from
// running forever. A 10s timeout is slow for a unit test, so it is skipped in
// short mode.
func TestVerifySandboxTimesOut(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping 10s sandbox timeout test in short mode")
	}
	requirePython3(t)
	caseDir := makeLintCase(t, t.TempDir(), lintTestBody, lintCaseOptions{})
	writeFile(t, filepath.Join(caseDir, "verify.py"),
		"import json, time\ncase = json.load(open(\"case.json\"))\ntime.sleep(60)\nprint(json.dumps({\"expected_number\": 9000.0}))\n")

	start := time.Now()
	_, code := captureOutput(t, func() int {
		return runVerify([]string{"--cases", filepath.Dir(caseDir)})
	})
	if code != 1 {
		t.Errorf("exit code = %d, want 1", code)
	}
	if elapsed := time.Since(start); elapsed > 45*time.Second {
		t.Errorf("verify took %s; the timeout did not fire", elapsed)
	}
}

func requirePython3(t *testing.T) {
	t.Helper()
	if _, err := exec.LookPath("python3"); err != nil {
		t.Skip("python3 not on PATH; bank verify runs case-supplied Python by design")
	}
}

// The bank file's bytes are its bank_version, which past reports quote. A
// re-run on the same cases must reproduce them exactly, which is only true if
// the encoder keeps Python's int-vs-float spelling and key sorting.
func TestBuildIsByteStable(t *testing.T) {
	casesRoot := filepath.Join(lab.RepoRoot(), "bench", "workbank", "cases")
	if _, err := os.Stat(casesRoot); err != nil {
		t.Skip("workbank cases not present")
	}
	first := filepath.Join(t.TempDir(), "a.json")
	second := filepath.Join(t.TempDir(), "b.json")
	captureOutput(t, func() int {
		return runBuild([]string{"--cases", casesRoot, "--status", "all", "--out", first})
	})
	captureOutput(t, func() int {
		return runBuild([]string{"--cases", casesRoot, "--status", "all", "--out", second})
	})
	a := mustReadFile(t, first)
	b := mustReadFile(t, second)
	if string(a) != string(b) {
		t.Error("two builds of the same cases produced different bytes")
	}
	if !strings.Contains(string(a), `"schema_version":5`) {
		t.Error("bank file is not the compact sorted-key encoding build.py produced")
	}
}

func mustReadFile(t *testing.T, path string) []byte {
	t.Helper()
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return data
}

// §4.3: a smalltalk case has no independently computable answer, so a missing
// verify.py is a skip, not a failure. Every other task type still fails.
func TestVerifySkipsSmalltalkWithoutVerifyPy(t *testing.T) {
	requirePython3(t)
	dir := t.TempDir()
	smalltalk := filepath.Join(dir, "nt-9001")
	writeCase(t, smalltalk, map[string]any{
		"task_type": "smalltalk", "scenario": "notool",
	})
	concept := filepath.Join(dir, "nt-9002")
	writeCase(t, concept, map[string]any{
		"task_type": "concept", "scenario": "notool",
	})

	out, code := captureOutput(t, func() int {
		return runVerify([]string{"--cases", dir})
	})
	if code != 1 {
		t.Errorf("exit code = %d, want 1 (only the concept case should fail)", code)
	}
	var report struct {
		Passed  int `json:"passed"`
		Failed  int `json:"failed"`
		Results []struct {
			Case   string `json:"case"`
			OK     bool   `json:"ok"`
			Checks []struct {
				Check   string `json:"check"`
				OK      bool   `json:"ok"`
				Warning string `json:"warning"`
				Error   string `json:"error"`
			} `json:"checks"`
		} `json:"results"`
	}
	if err := json.Unmarshal([]byte(out), &report); err != nil {
		t.Fatalf("report is not JSON: %v\n%s", err, out)
	}
	if report.Passed != 1 || report.Failed != 1 {
		t.Fatalf("passed/failed = %d/%d, want 1/1\n%s", report.Passed, report.Failed, out)
	}
	for _, result := range report.Results {
		switch result.Case {
		case "nt-9001":
			if !result.OK {
				t.Errorf("smalltalk case failed: %+v", result.Checks)
			}
			if len(result.Checks) != 1 || result.Checks[0].Warning != "verify_skipped_smalltalk" {
				t.Errorf("smalltalk checks = %+v, want the skip warning", result.Checks)
			}
		case "nt-9002":
			if result.OK {
				t.Error("a concept case without verify.py passed; only smalltalk is exempt")
			}
		default:
			t.Errorf("unexpected case in report: %s", result.Case)
		}
	}
}

func writeCase(t *testing.T, dir string, tags map[string]any) {
	t.Helper()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	caseObj := map[string]any{
		"id":          filepath.Base(dir),
		"description": "test case " + filepath.Base(dir),
		"tags":        tags,
		"files":       map[string]any{},
		"turns":       []any{map[string]any{"prompt": "hi", "expect": map[string]any{"tools": []any{}}}},
	}
	data, err := json.MarshalIndent(caseObj, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "case.json"), data, 0o644); err != nil {
		t.Fatal(err)
	}
}

// writeVerifyShapeCase writes a case.json from a raw object plus a verify.py,
// so shape-recognition tests can exercise real verify.py runs in a temp dir
// (same discipline as TestVerifySkipsSmalltalkWithoutVerifyPy: cases are never
// added to testdata, which TestVerifyTestdata pins at 3).
func writeVerifyShapeCase(t *testing.T, dir string, caseObj map[string]any, verifyPy string) {
	t.Helper()
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	if _, ok := caseObj["id"]; !ok {
		caseObj["id"] = filepath.Base(dir)
	}
	if _, ok := caseObj["tags"]; !ok {
		caseObj["tags"] = map[string]any{"scenario": "notool", "task_type": "snippet_in_reply"}
	}
	data, err := json.Marshal(caseObj)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "case.json"), data, 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "verify.py"), []byte(verifyPy), 0o644); err != nil {
		t.Fatal(err)
	}
}

type shapeReport struct {
	Passed  int `json:"passed"`
	Failed  int `json:"failed"`
	Results []struct {
		Case   string `json:"case"`
		OK     bool   `json:"ok"`
		Checks []struct {
			Check   string `json:"check"`
			OK      bool   `json:"ok"`
			Warning string `json:"warning"`
			Error   string `json:"error"`
			Detail  any    `json:"detail"`
		} `json:"checks"`
	} `json:"results"`
}

func parseShapeReport(t *testing.T, out string) shapeReport {
	t.Helper()
	var report shapeReport
	if err := json.Unmarshal([]byte(out), &report); err != nil {
		t.Fatalf("report is not JSON: %v\n%s", err, out)
	}
	return report
}

func findResult(r shapeReport, caseID string) *struct {
	Case   string `json:"case"`
	OK     bool   `json:"ok"`
	Checks []struct {
		Check   string `json:"check"`
		OK      bool   `json:"ok"`
		Warning string `json:"warning"`
		Error   string `json:"error"`
		Detail  any    `json:"detail"`
	} `json:"checks"`
} {
	for i := range r.Results {
		if r.Results[i].Case == caseID {
			return &r.Results[i]
		}
	}
	return nil
}

// A-group: verify.py re-derives the acceptable keyword forms from the fixture
// and the output is compared to expect.output_contains_any as a set. nt-5278
// was the live instance of the mismatch case (verify had more, expect less).
func TestVerifyRecognizesContainsAnyShape(t *testing.T) {
	requirePython3(t)
	dir := t.TempDir()
	expect := map[string]any{"output_contains_any": []any{"ALPHA", "BETA"}}
	pos := filepath.Join(dir, "nt-7001")
	writeVerifyShapeCase(t, pos, map[string]any{
		"turns": []any{map[string]any{"prompt": "p", "expect": expect}},
	}, "import json\nprint(json.dumps({\"expected_contains_any\": [\"BETA\", \"ALPHA\"]}))\n")
	neg := filepath.Join(dir, "nt-7002")
	writeVerifyShapeCase(t, neg, map[string]any{
		"turns": []any{map[string]any{"prompt": "p", "expect": expect}},
	}, "import json\nprint(json.dumps({\"expected_contains_any\": [\"ALPHA\", \"BETA\", \"GAMMA\"]}))\n")

	out, code := captureOutput(t, func() int {
		return runVerify([]string{"--cases", dir})
	})
	if code != 1 {
		t.Fatalf("exit code = %d, want 1 (the mismatch case fails)\n%s", code, out)
	}
	report := parseShapeReport(t, out)
	if pos := findResult(report, "nt-7001"); pos == nil || !pos.OK {
		t.Errorf("nt-7001 should pass: %+v", pos)
	} else {
		found := false
		for _, c := range pos.Checks {
			if c.Check == "expect_match" && c.OK {
				found = true
			}
			if c.Warning == "verify_shape_unknown" {
				t.Errorf("nt-7001 still carries the unknown warning: %+v", pos.Checks)
			}
		}
		if !found {
			t.Errorf("nt-7001 has no passing expect_match check: %+v", pos.Checks)
		}
	}
	if neg := findResult(report, "nt-7002"); neg == nil || neg.OK {
		t.Errorf("nt-7002 should fail: %+v", neg)
	} else {
		mismatch := false
		for _, c := range neg.Checks {
			if c.Check == "expect_match" && !c.OK && strings.Contains(fmt.Sprint(c.Detail), "GAMMA") {
				mismatch = true
			}
		}
		if !mismatch {
			t.Errorf("nt-7002 mismatch detail does not name the extra element: %+v", neg.Checks)
		}
	}
}

// B-group: a snapshot dict holding expect.run.expected_stdout is a known shape
// (run_expect_match already proved it); it must not be reported as unknown.
func TestVerifyRecognizesExpectedStdoutShape(t *testing.T) {
	requirePython3(t)
	dir := t.TempDir()
	caseDir := filepath.Join(dir, "cfg-7003")
	writeVerifyShapeCase(t, caseDir, map[string]any{
		"turns":  []any{map[string]any{"prompt": "p", "expect": map[string]any{}}},
		"expect": map[string]any{"run": map[string]any{"expected_stdout": "250"}},
	}, "import json\nprint(json.dumps({\"expected_stdout\": \"250\"}))\n")

	out, code := captureOutput(t, func() int {
		return runVerify([]string{"--cases", dir})
	})
	if code != 0 {
		t.Fatalf("exit code = %d, want 0\n%s", code, out)
	}
	report := parseShapeReport(t, out)
	result := findResult(report, "cfg-7003")
	if result == nil || !result.OK {
		t.Fatalf("cfg-7003 should pass: %+v", result)
	}
	for _, c := range result.Checks {
		if c.Warning == "verify_shape_unknown" || c.Error == "verify_shape_unknown" {
			t.Errorf("cfg-7003 reported as unknown shape: %+v", result.Checks)
		}
		if c.Check == "expect_match" && !c.OK {
			t.Errorf("cfg-7003 expect_match failed: %+v", result.Checks)
		}
	}
}

// C-group: refusal-shaped cases (no value expectation anywhere) have nothing
// for verify.py to recompute, so the snapshot output is a skip, not unknown,
// and the sabotage test does not run.
func TestVerifySkipsRefusalShape(t *testing.T) {
	requirePython3(t)
	dir := t.TempDir()
	caseDir := filepath.Join(dir, "nt-7004")
	writeVerifyShapeCase(t, caseDir, map[string]any{
		"turns": []any{map[string]any{"prompt": "p", "expect": map[string]any{
			"forbidden_tools":     []any{"ssh"},
			"output_contains_any": []any{"cannot", "can't"},
		}}},
	}, "import json\nprint(json.dumps({\"refusal_words\": [\"cannot\"], \"requested_operation\": \"restart nginx\"}))\n")

	out, code := captureOutput(t, func() int {
		return runVerify([]string{"--cases", dir})
	})
	if code != 0 {
		t.Fatalf("exit code = %d, want 0\n%s", code, out)
	}
	report := parseShapeReport(t, out)
	result := findResult(report, "nt-7004")
	if result == nil || !result.OK {
		t.Fatalf("nt-7004 should pass: %+v", result)
	}
	if len(result.Checks) != 1 || result.Checks[0].Warning != "verify_skipped_refusal" {
		t.Errorf("nt-7004 checks = %+v, want the single refusal skip", result.Checks)
	}
}

// C-group negative: the moment a value expectation appears the case is no
// longer refusal-shaped, so it is not skipped -- and --strict-shape fails it.
func TestVerifyRefusalShapeWithNumberExpectationNotSkipped(t *testing.T) {
	requirePython3(t)
	dir := t.TempDir()
	caseDir := filepath.Join(dir, "nt-7005")
	writeVerifyShapeCase(t, caseDir, map[string]any{
		"turns": []any{map[string]any{"prompt": "p", "expect": map[string]any{
			"forbidden_tools":     []any{"ssh"},
			"output_contains_any": []any{"cannot", "can't"},
			"expected_number":     42,
		}}},
	}, "import json\nprint(json.dumps({\"refusal_words\": [\"cannot\"]}))\n")

	out, code := captureOutput(t, func() int {
		return runVerify([]string{"--cases", dir})
	})
	if code != 0 {
		t.Fatalf("default mode: exit code = %d, want 0\n%s", code, out)
	}
	report := parseShapeReport(t, out)
	if result := findResult(report, "nt-7005"); result == nil || !result.OK {
		t.Errorf("default mode should keep nt-7005 passing with a warning: %+v", result)
	}

	out, code = captureOutput(t, func() int {
		return runVerify([]string{"--cases", dir, "--strict-shape"})
	})
	if code != 1 {
		t.Fatalf("strict mode: exit code = %d, want 1\n%s", code, out)
	}
	report = parseShapeReport(t, out)
	result := findResult(report, "nt-7005")
	if result == nil || result.OK {
		t.Fatalf("strict mode should fail nt-7005: %+v", result)
	}
	unknown := false
	for _, c := range result.Checks {
		if c.Check == "verify_shape" && !c.OK && c.Error == "verify_shape_unknown" {
			unknown = true
		}
		if c.Warning == "verify_skipped_refusal" {
			t.Errorf("nt-7005 was skipped as refusal despite expected_number: %+v", result.Checks)
		}
	}
	if !unknown {
		t.Errorf("strict mode did not record verify_shape_unknown: %+v", result.Checks)
	}
}

// --strict-shape turns every remaining unknown shape into a failure; the
// default keeps the historical warning + pass.
func TestVerifyStrictShapeFailsUnknown(t *testing.T) {
	requirePython3(t)
	dir := t.TempDir()
	caseDir := filepath.Join(dir, "nt-7006")
	writeVerifyShapeCase(t, caseDir, map[string]any{
		"turns": []any{map[string]any{"prompt": "p", "expect": map[string]any{}}},
	}, "import json\nprint(json.dumps({\"foo\": 1}))\n")

	out, code := captureOutput(t, func() int {
		return runVerify([]string{"--cases", dir})
	})
	if code != 0 {
		t.Fatalf("default mode: exit code = %d, want 0\n%s", code, out)
	}
	report := parseShapeReport(t, out)
	if result := findResult(report, "nt-7006"); result == nil || !result.OK {
		t.Errorf("default mode should pass with a warning: %+v", result)
	}

	out, code = captureOutput(t, func() int {
		return runVerify([]string{"--cases", dir, "--strict-shape"})
	})
	if code != 1 {
		t.Fatalf("strict mode: exit code = %d, want 1\n%s", code, out)
	}
	report = parseShapeReport(t, out)
	if result := findResult(report, "nt-7006"); result == nil || result.OK {
		t.Errorf("strict mode should fail nt-7006: %+v", result)
	}
}
