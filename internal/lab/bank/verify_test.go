package bank

import (
	"encoding/json"
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
