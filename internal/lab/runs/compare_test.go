package runs

import (
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// captureCompareRun runs fn with both streams captured. stderr is the package
// variable the commands write errors to, not os.Stderr.
func captureCompareRun(t *testing.T, fn func() int) (stdout, stderrText string, code int) {
	t.Helper()
	oldOut, oldErr, oldStderr := os.Stdout, os.Stderr, stderr
	outR, outW, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	errR, errW, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	os.Stdout, os.Stderr, stderr = outW, errW, errW
	code = fn()
	outW.Close()
	errW.Close()
	os.Stdout, os.Stderr, stderr = oldOut, oldErr, oldStderr
	outData, _ := io.ReadAll(outR)
	errData, _ := io.ReadAll(errR)
	outR.Close()
	errR.Close()
	return string(outData), string(errData), code
}

// makeCompareRunDir writes a minimal run directory: run.json + summary.json
// with one entry per id, passed taken from passSet.
func makeCompareRunDir(t *testing.T, dir string, ids []string, passSet map[string]bool) {
	t.Helper()
	manifestCases := make([]any, 0, len(ids))
	summaryCases := make([]any, 0, len(ids))
	for _, id := range ids {
		manifestCases = append(manifestCases, map[string]any{
			"id":   id,
			"tags": map[string]any{"family": "fam-" + strings.SplitN(id, "-", 2)[0]},
		})
		summaryCases = append(summaryCases, map[string]any{
			"id":     id,
			"passed": passSet[id],
			"tags":   map[string]any{},
		})
	}
	writeJSONFile(t, filepath.Join(dir, "run.json"), map[string]any{"cases": manifestCases})
	writeJSONFile(t, filepath.Join(dir, "summary.json"), map[string]any{"cases": summaryCases})
}

func writeJSONFile(t *testing.T, path string, value any) {
	t.Helper()
	data, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, data, 0o600); err != nil {
		t.Fatal(err)
	}
}

// decodeFirstReport parses the leading JSON value of compare's stdout.
func decodeFirstReport(t *testing.T, stdout string) map[string]any {
	t.Helper()
	dec := json.NewDecoder(strings.NewReader(stdout))
	var report map[string]any
	if err := dec.Decode(&report); err != nil {
		t.Fatalf("stdout does not start with a JSON report: %v\n%s", err, stdout)
	}
	return report
}

func compareFlips(t *testing.T, report map[string]any, key string) []string {
	t.Helper()
	flips := report["flips"].(map[string]any)
	entries := flips[key].([]any)
	out := make([]string, 0, len(entries))
	for _, e := range entries {
		out = append(out, e.(map[string]any)["case"].(string))
	}
	return out
}

// M1: the seed list must track the training data it describes. base700's
// parent_seed_id set drifting from seeded-base700.txt means the exclusion list
// no longer covers (or over-covers) the actual leak.
func TestSeedListMatchesBase700Archive(t *testing.T) {
	const (
		archivePath  = "../../../bench/archive/workspace-agent-700-20260920/generated/normalized/all.jsonl"
		seedListPath = "../../../bench/workbank/seeded-base700.txt"
	)
	data, err := os.ReadFile(archivePath)
	if err != nil {
		t.Fatal(err)
	}
	archiveSeeds := map[string]bool{}
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		var row map[string]any
		if err := json.Unmarshal([]byte(line), &row); err != nil {
			t.Fatalf("bad archive row: %v", err)
		}
		if id, ok := row["parent_seed_id"].(string); ok && id != "" {
			archiveSeeds[id] = true
		}
	}
	ids, err := readExcludeFile(seedListPath)
	if err != nil {
		t.Fatal(err)
	}
	listSeeds := map[string]bool{}
	for _, id := range ids {
		listSeeds[id] = true
	}
	if len(archiveSeeds) != len(listSeeds) {
		t.Fatalf("seed count drifted: archive %d, list %d", len(archiveSeeds), len(listSeeds))
	}
	for id := range archiveSeeds {
		if !listSeeds[id] {
			t.Errorf("archive seed %s missing from seeded-base700.txt", id)
		}
	}
	for id := range listSeeds {
		if !archiveSeeds[id] {
			t.Errorf("seeded-base700.txt lists %s which is not a parent_seed_id in the archive", id)
		}
	}
}

func TestCompareExcludeCases(t *testing.T) {
	ids := []string{"aaa-0001", "aaa-0002", "aaa-0003", "aaa-0004"}
	aPass := map[string]bool{"aaa-0001": true, "aaa-0002": true, "aaa-0003": false, "aaa-0004": true}
	bPass := map[string]bool{"aaa-0001": true, "aaa-0002": false, "aaa-0003": false, "aaa-0004": true}

	base := t.TempDir()
	dirA := filepath.Join(base, "a")
	dirB := filepath.Join(base, "b")
	if err := os.MkdirAll(dirA, 0o700); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(dirB, 0o700); err != nil {
		t.Fatal(err)
	}
	makeCompareRunDir(t, dirA, ids, aPass)
	makeCompareRunDir(t, dirB, ids, bPass)

	// Without the flag: the three new keys are present, everything else as before.
	stdout, stderrText, code := captureCompareRun(t, func() int {
		return RunCompare(CompareArgs{A: dirA, B: dirB})
	})
	if code != 0 {
		t.Fatalf("code = %d, stderr: %s", code, stderrText)
	}
	if strings.Contains(stderrText, "warning") {
		t.Errorf("unexpected stderr without the flag: %s", stderrText)
	}
	report := decodeFirstReport(t, stdout)
	if got := report["excluded_cases"]; got != float64(0) {
		t.Errorf("excluded_cases = %v, want 0", got)
	}
	if got, ok := report["exclude_file"]; !ok || got != nil {
		t.Errorf("exclude_file = %v (ok=%v), want null", got, ok)
	}
	passed := report["passed"].(map[string]any)
	if passed["a"] != float64(3) || passed["b"] != float64(2) {
		t.Errorf("passed = %v, want a=3 b=2", passed)
	}
	if got := report["common_cases"]; got != float64(4) {
		t.Errorf("common_cases = %v, want 4", got)
	}
	if flips := compareFlips(t, report, "a_pass_b_fail"); len(flips) != 1 || flips[0] != "aaa-0002" {
		t.Errorf("a_pass_b_fail = %v, want [aaa-0002]", flips)
	}

	// With the flag: aaa-0002 is dropped on both sides before common, passed,
	// flips and bootstrap are computed; aaa-9999 is absent and warned about.
	excludePath := filepath.Join(base, "excluded.txt")
	excludeText := "# comment line\n\naaa-0002\naaa-9999\n"
	if err := os.WriteFile(excludePath, []byte(excludeText), 0o600); err != nil {
		t.Fatal(err)
	}
	stdout, stderrText, code = captureCompareRun(t, func() int {
		return RunCompare(CompareArgs{A: dirA, B: dirB, ExcludeCases: excludePath})
	})
	if code != 0 {
		t.Fatalf("code = %d, stderr: %s", code, stderrText)
	}
	if want := "warning: 1 excluded ids not present in either side\n"; !strings.Contains(stderrText, want) {
		t.Errorf("stderr = %q, want it to contain %q", stderrText, want)
	}
	if !strings.Contains(stdout, "excluded: 1 cases from "+excludePath+"\n") {
		t.Errorf("stdout missing the excluded line:\n%s", stdout)
	}
	report = decodeFirstReport(t, stdout)
	if got := report["excluded_cases"]; got != float64(1) {
		t.Errorf("excluded_cases = %v, want 1", got)
	}
	if got := report["exclude_file"]; got != excludePath {
		t.Errorf("exclude_file = %v, want %s", got, excludePath)
	}
	passed = report["passed"].(map[string]any)
	if passed["a"] != float64(2) || passed["b"] != float64(2) {
		t.Errorf("passed = %v, want a=2 b=2", passed)
	}
	if got := report["common_cases"]; got != float64(3) {
		t.Errorf("common_cases = %v, want 3", got)
	}
	if flips := compareFlips(t, report, "a_pass_b_fail"); len(flips) != 0 {
		t.Errorf("a_pass_b_fail = %v, want empty", flips)
	}

	// The new keys sit right after common_cases: downstream diffs are keyed on
	// insertion order.
	raw := strings.SplitN(stdout, "\n", 2)[1] // skip the opening brace line
	order := []string{`"common_cases"`, `"excluded_cases"`, `"exclude_file"`, `"passed"`, `"pass_rate"`}
	last := -1
	for _, key := range order {
		idx := strings.Index(raw, key)
		if idx < 0 {
			t.Fatalf("key %s missing from report:\n%s", key, stdout)
		}
		if idx < last {
			t.Errorf("key %s out of order:\n%s", key, stdout)
		}
		last = idx
	}
}

func TestCompareExcludeFileValidation(t *testing.T) {
	ids := []string{"aaa-0001", "aaa-0002"}
	base := t.TempDir()
	dirA := filepath.Join(base, "a")
	dirB := filepath.Join(base, "b")
	if err := os.MkdirAll(dirA, 0o700); err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(dirB, 0o700); err != nil {
		t.Fatal(err)
	}
	pass := map[string]bool{"aaa-0001": true, "aaa-0002": false}
	makeCompareRunDir(t, dirA, ids, pass)
	makeCompareRunDir(t, dirB, ids, pass)

	for _, tc := range []struct {
		name    string
		content string
	}{
		{"uppercase and trailing space", "CFG-0001 \n"},
		{"wrong digit count", "cfg-01\n"},
		{"underscore id", "cfg_0001\n"},
	} {
		t.Run(tc.name, func(t *testing.T) {
			excludePath := filepath.Join(base, tc.name+".txt")
			if err := os.WriteFile(excludePath, []byte(tc.content), 0o600); err != nil {
				t.Fatal(err)
			}
			_, stderrText, code := captureCompareRun(t, func() int {
				return RunCompare(CompareArgs{A: dirA, B: dirB, ExcludeCases: excludePath})
			})
			if code != 2 {
				t.Errorf("code = %d, want 2 (stderr: %s)", code, stderrText)
			}
		})
	}

	t.Run("unreadable file", func(t *testing.T) {
		_, _, code := captureCompareRun(t, func() int {
			return RunCompare(CompareArgs{A: dirA, B: dirB,
				ExcludeCases: filepath.Join(base, "does-not-exist.txt")})
		})
		if code != 2 {
			t.Errorf("code = %d, want 2", code)
		}
	})
}
