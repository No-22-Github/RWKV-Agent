package bank

import (
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// These are the cases from the former lint regression suite, ported one for
// one (docs/go-tooling-migration.md §6 M2). Each covers a defect class the
// bank actually shipped: nt-0001's stale notes, scr-0004's hidden set outside
// the workspace, and a notool case carrying a TR-NOTOOLNEED phrase.

const (
	lintTestBody = "A monitoring dashboard reports an ingest rate of 2.5 MiB per second. " +
		"Express that same rate in MiB per hour. "
	lintTestNotes = `## Traps
- None.
## Reference solution
No steps; ref_calls is 0. 2.5 * 3600 = 9000; answer 9000.
## Why the answer is unique
The prompt supplies every input.
`
	lintTestVerify = `import json
case = json.load(open("case.json"))
print(json.dumps({"expected_number": 9000.0}))
`
)

// lintTestContract is the mandated answer contract from the vocabulary.
func lintTestContract(t *testing.T) string {
	t.Helper()
	raw, err := os.ReadFile(DefaultVocab())
	if err != nil {
		t.Fatalf("read vocab: %v", err)
	}
	var obj map[string]any
	if err := json.Unmarshal(raw, &obj); err != nil {
		t.Fatalf("parse vocab: %v", err)
	}
	contracts, _ := obj["answer_contracts"].(map[string]any)
	contract, _ := contracts["unknown"].(string)
	if contract == "" {
		t.Fatal("vocab has no answer_contracts.unknown")
	}
	return contract
}

type lintCaseOptions struct {
	notes      string
	expect     map[string]any
	caseExpect map[string]any
}

// makeLintCase writes a case under root/notool/nt-9001, mirroring test_lint.py's
// make_case helper.
func makeLintCase(t *testing.T, root, promptBody string, opts lintCaseOptions) string {
	t.Helper()
	caseDir := filepath.Join(root, "notool", "nt-9001")
	if err := os.MkdirAll(caseDir, 0o755); err != nil {
		t.Fatal(err)
	}
	expect := opts.expect
	if expect == nil {
		expect = map[string]any{
			"expected_number": 9000.0,
			"tolerance":       0.01,
			"tools":           []any{},
		}
	}
	caseObj := map[string]any{
		"id":          "nt-9001",
		"description": "Convert a steady throughput; zero tool calls. WORKBANK-CANARY-0123abcd",
		"category":    "notool",
		"tags": map[string]any{
			"scenario":      "notool",
			"task_type":     "unit_convert",
			"traps":         []any{},
			"trap_decoys":   map[string]any{},
			"axes":          []any{"DEC"},
			"level":         "L0",
			"ref_calls":     0,
			"fixture_bytes": 0,
			"status":        "draft",
			"version":       1,
			"author":        "llm:test",
			"reviewer":      "human:test",
		},
		"files":       map[string]any{},
		"web_fixture": []any{},
		"turns": []any{map[string]any{
			"prompt": promptBody + lintTestContract(t),
			"expect": expect,
		}},
	}
	if opts.caseExpect != nil {
		caseObj["expect"] = opts.caseExpect
	}
	writeJSON(t, filepath.Join(caseDir, "case.json"), caseObj)
	notes := opts.notes
	if notes == "" {
		notes = lintTestNotes
	}
	writeFile(t, filepath.Join(caseDir, "NOTES.md"), notes)
	writeFile(t, filepath.Join(caseDir, "verify.py"), lintTestVerify)
	return caseDir
}

// runLintCase runs bank lint on one case dir and returns its exit code and the
// parsed violations, with stdout and stderr captured.
func runLintCase(t *testing.T, caseDir string) (int, []map[string]any) {
	t.Helper()
	return runLintArgs(t, "--case", caseDir, "--vocab", DefaultVocab())
}

// runLintArgs is runLintCase for tests that pass extra flags (--canary-prefix,
// --cases).
func runLintArgs(t *testing.T, args ...string) (int, []map[string]any) {
	t.Helper()
	out, code := captureOutput(t, func() int {
		return runLint(args)
	})
	var violations []map[string]any
	for _, line := range strings.Split(out, "\n") {
		if strings.TrimSpace(line) == "" {
			continue
		}
		var item map[string]any
		if err := json.Unmarshal([]byte(line), &item); err != nil {
			t.Fatalf("violation line is not JSON: %s", line)
		}
		violations = append(violations, item)
	}
	return code, violations
}

func hasRule(violations []map[string]any, rule string) bool {
	for _, v := range violations {
		if v["rule"] == rule {
			return true
		}
	}
	return false
}

func lintBody(t *testing.T, body string) (int, []map[string]any) {
	t.Helper()
	return runLintCase(t, makeLintCase(t, t.TempDir(), body, lintCaseOptions{}))
}

// "Without using any tools" must trip TR-NOTOOLNEED's "without tools" even
// though the case declares no traps: notool is intrinsic to the scenario.
func TestLintForbiddenWordMatchesInterveningWords(t *testing.T) {
	failed, violations := lintBody(t,
		"A dashboard shows 2.5 MiB per second. Without using any tools, "+
			"express that rate in MiB per hour. ")
	if failed != 1 {
		t.Errorf("exit code = %d, want 1", failed)
	}
	found := false
	for _, v := range violations {
		if v["rule"] == "prompt.forbidden_word" &&
			strings.Contains(v["detail"].(string), "without tools") {
			found = true
		}
	}
	if !found {
		t.Errorf("no prompt.forbidden_word for 'without tools': %v", violations)
	}
}

func TestLintCleanPromptPasses(t *testing.T) {
	failed, violations := lintBody(t, lintTestBody)
	if len(violations) != 0 {
		t.Errorf("unexpected violations: %v", violations)
	}
	if failed != 0 {
		t.Errorf("exit code = %d, want 0", failed)
	}
}

func TestLintToolNameInPromptFails(t *testing.T) {
	failed, violations := lintBody(t, lintTestBody+"Use read_file to confirm. ")
	if failed != 1 {
		t.Errorf("exit code = %d, want 1", failed)
	}
	if !hasRule(violations, "prompt.tool_name") {
		t.Errorf("no prompt.tool_name violation: %v", violations)
	}
}

// NOTES.md must state the answer case.json scores: the nt-0001 defect class.
func TestLintNotesMissingExpectedNumberFails(t *testing.T) {
	notes := strings.Replace(lintTestNotes, " 2.5 * 3600 = 9000; answer 9000.", "", 1)
	_, violations := runLintCase(t, makeLintCase(t, t.TempDir(), lintTestBody,
		lintCaseOptions{notes: notes}))
	if !hasRule(violations, "notes.answer") {
		t.Errorf("no notes.answer violation: %v", violations)
	}
}

func TestLintNotesStatingExpectedNumberPasses(t *testing.T) {
	failed, violations := lintBody(t, lintTestBody)
	if len(violations) != 0 {
		t.Errorf("unexpected violations: %v", violations)
	}
	if failed != 0 {
		t.Errorf("exit code = %d, want 0", failed)
	}
}

func TestLintNotesMustStateOutputEqualsAnswer(t *testing.T) {
	_, violations := runLintCase(t, makeLintCase(t, t.TempDir(), lintTestBody, lintCaseOptions{
		expect: map[string]any{"output_equals": "443", "tools": []any{}},
	}))
	if !hasRule(violations, "notes.answer") {
		t.Errorf("no notes.answer violation: %v", violations)
	}
}

// scr-0004's defect class: a hidden set outside the project tree.
func TestLintEscapingHiddenPathFails(t *testing.T) {
	for _, bad := range []string{"../hidden/extra.csv", "/tmp/extra.csv"} {
		_, violations := runLintCase(t, makeLintCase(t, t.TempDir(), lintTestBody, lintCaseOptions{
			caseExpect: map[string]any{
				"run": map[string]any{
					"path":            "report.py",
					"hidden_files":    map[string]any{bad: "a,b\n"},
					"expected_stdout": "ok",
				},
			},
		}))
		if !hasRule(violations, "expect.run.hidden") {
			t.Errorf("hidden path %q: no expect.run.hidden violation: %v", bad, violations)
		}
	}
}

func TestLintNestedHiddenPathPasses(t *testing.T) {
	_, violations := runLintCase(t, makeLintCase(t, t.TempDir(), lintTestBody, lintCaseOptions{
		caseExpect: map[string]any{
			"run": map[string]any{
				"path":            "report.py",
				"hidden_files":    map[string]any{"batches/2026-09/extra.csv": "a,b\n"},
				"expected_stdout": "ok",
			},
		},
	}))
	if hasRule(violations, "expect.run.hidden") {
		t.Errorf("unexpected expect.run.hidden violation: %v", violations)
	}
}

func writeJSON(t *testing.T, path string, v any) {
	t.Helper()
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	writeFile(t, path, string(data)+"\n")
}

func writeFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

// captureOutput runs fn with stdout captured and stderr discarded, returning
// what was written to stdout. The two streams stay separate because the tools'
// summaries are stderr and their payload is stdout (§4.2).
func captureOutput(t *testing.T, fn func() int) (string, int) {
	t.Helper()
	oldOut, oldErr := os.Stdout, os.Stderr
	r, w, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	devNull, err := os.OpenFile(os.DevNull, os.O_WRONLY, 0)
	if err != nil {
		t.Fatal(err)
	}
	os.Stdout, os.Stderr = w, devNull
	code := fn()
	w.Close()
	devNull.Close()
	os.Stdout, os.Stderr = oldOut, oldErr
	data, _ := io.ReadAll(r)
	return string(data), code
}

// --fix must write the computed byte count into tags.fixture_bytes. The first
// port wrote the top-level (absent) key instead, so every fixed case came back
// with fixture_bytes: null and failed the next lint.
func TestLintFixBackfillsFixtureBytes(t *testing.T) {
	caseDir := makeLintCase(t, t.TempDir(), lintTestBody, lintCaseOptions{})
	path := filepath.Join(caseDir, "case.json")
	var caseObj map[string]any
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(raw, &caseObj); err != nil {
		t.Fatal(err)
	}
	caseObj["files"] = map[string]any{"rates.txt": "ingest 2.5 MiB/s\n"}
	writeJSON(t, path, caseObj)

	captureOutput(t, func() int {
		return runLint([]string{"--fix", "--case", caseDir, "--vocab", DefaultVocab()})
	})
	raw, err = os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var fixed map[string]any
	if err := json.Unmarshal(raw, &fixed); err != nil {
		t.Fatal(err)
	}
	if got := fixed["tags"].(map[string]any)["fixture_bytes"]; got != float64(17) {
		t.Fatalf("fixture_bytes after --fix = %v, want 17", got)
	}
	if _, violations := runLintCase(t, caseDir); hasRule(violations, "fixture_bytes") {
		t.Fatalf("lint still reports fixture_bytes after --fix: %v", violations)
	}
}

// -- canary prefix and smalltalk (docs/distill-workflow.md §4.1, §4.3) --------

// distillCanaryPrefix is what the distillation tree replaces WORKBANK-CANARY
// with: the test-bank canary means "never train on this" (§2.2).
const distillCanaryPrefix = "DISTILL-CANARY"

// distillCaseDir returns bench/distill/cases/notool/<id>, skipping the test in
// checkouts that do not carry the bench tree.
func distillCaseDir(t *testing.T, id string) string {
	t.Helper()
	dir := filepath.Join(lab.RepoRoot(), "bench", "distill", "cases", "notool", id)
	if _, err := os.Stat(filepath.Join(dir, "case.json")); err != nil {
		t.Skipf("distill case %s not present", id)
	}
	return dir
}

// copyCaseDir copies a case into <tmp>/<scenario>/<id>/ so a test can mutate it
// without touching bench/.
func copyCaseDir(t *testing.T, srcDir string) string {
	t.Helper()
	dst := filepath.Join(t.TempDir(), filepath.Base(filepath.Dir(srcDir)), filepath.Base(srcDir))
	if err := os.MkdirAll(dst, 0o755); err != nil {
		t.Fatal(err)
	}
	for _, name := range []string{"case.json", "verify.py", "NOTES.md"} {
		data, err := os.ReadFile(filepath.Join(srcDir, name))
		if err != nil {
			continue // not every case carries all three files
		}
		writeFile(t, filepath.Join(dst, name), string(data))
	}
	return dst
}

// editCaseJSON rewrites a copied case.json through edit.
func editCaseJSON(t *testing.T, caseDir string, edit func(map[string]any)) {
	t.Helper()
	path := filepath.Join(caseDir, "case.json")
	raw, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	var caseObj map[string]any
	if err := json.Unmarshal(raw, &caseObj); err != nil {
		t.Fatal(err)
	}
	edit(caseObj)
	writeJSON(t, path, caseObj)
}

// §4.1/§4.3: the five smalltalk smoke cases are clean once the canary rule
// takes the flag and smalltalk's exemptions apply.
func TestLintDistillSmalltalkCasesClean(t *testing.T) {
	for _, id := range []string{"nt-5001", "nt-5002", "nt-5003", "nt-5004", "nt-5005"} {
		code, violations := runLintArgs(t, "--case", distillCaseDir(t, id),
			"--vocab", DefaultVocab(), "--canary-prefix", distillCanaryPrefix)
		if code != 0 || len(violations) != 0 {
			t.Errorf("%s: exit code = %d, violations = %v", id, code, violations)
		}
	}
}

// §4.1 negative: a description still carrying the test-bank canary fails both
// the prefix rule and the foreign-canary rule.
func TestLintDistillCanaryWrongPrefixFailsBothRules(t *testing.T) {
	caseDir := copyCaseDir(t, distillCaseDir(t, "nt-5001"))
	editCaseJSON(t, caseDir, func(caseObj map[string]any) {
		desc, _ := caseObj["description"].(string)
		caseObj["description"] = strings.Replace(desc, distillCanaryPrefix+"-", "WORKBANK-CANARY-", 1)
	})
	code, violations := runLintArgs(t, "--case", caseDir, "--vocab", DefaultVocab(),
		"--canary-prefix", distillCanaryPrefix)
	if code != 1 {
		t.Errorf("exit code = %d, want 1", code)
	}
	for _, rule := range []string{"canary", "canary.foreign"} {
		if !hasRule(violations, rule) {
			t.Errorf("no %s violation: %v", rule, violations)
		}
	}
}

// §4.1 negative: WORKBANK-CANARY left in verify.py or NOTES.md is reported too.
func TestLintForeignCanaryInVerifyPyOrNotes(t *testing.T) {
	for _, file := range []string{"verify.py", "NOTES.md"} {
		caseDir := copyCaseDir(t, distillCaseDir(t, "nt-5001"))
		path := filepath.Join(caseDir, file)
		existing, _ := os.ReadFile(path)
		writeFile(t, path, string(existing)+"# WORKBANK-CANARY-xxxxxxxx leftover\n")
		code, violations := runLintArgs(t, "--case", caseDir, "--vocab", DefaultVocab(),
			"--canary-prefix", distillCanaryPrefix)
		if code != 1 {
			t.Errorf("%s: exit code = %d, want 1", file, code)
		}
		if !hasRule(violations, "canary.foreign") {
			t.Errorf("%s: no canary.foreign violation: %v", file, violations)
		}
	}
}

// §4.3 negative: a smalltalk case with an answer contract is the violation,
// and the plain answer_contract rule must stay silent.
func TestLintSmalltalkAnswerContractFails(t *testing.T) {
	caseDir := copyCaseDir(t, distillCaseDir(t, "nt-5001"))
	contract := lintTestContract(t)
	editCaseJSON(t, caseDir, func(caseObj map[string]any) {
		turns, _ := caseObj["turns"].([]any)
		last, _ := turns[len(turns)-1].(map[string]any)
		prompt, _ := last["prompt"].(string)
		last["prompt"] = prompt + " " + contract
	})
	code, violations := runLintArgs(t, "--case", caseDir, "--vocab", DefaultVocab(),
		"--canary-prefix", distillCanaryPrefix)
	if code != 1 {
		t.Errorf("exit code = %d, want 1", code)
	}
	if !hasRule(violations, "answer_contract.smalltalk") {
		t.Errorf("no answer_contract.smalltalk violation: %v", violations)
	}
	if hasRule(violations, "answer_contract") {
		t.Errorf("plain answer_contract must not fire for smalltalk: %v", violations)
	}
}

// §4.3 negative: every smalltalk turn must demand tools/[],
// require_active_no_call and a non-empty keyword list.
func TestLintSmalltalkMissingOutputContainsAnyFails(t *testing.T) {
	caseDir := copyCaseDir(t, distillCaseDir(t, "nt-5001"))
	editCaseJSON(t, caseDir, func(caseObj map[string]any) {
		turns, _ := caseObj["turns"].([]any)
		turn, _ := turns[len(turns)-1].(map[string]any)
		expect, _ := turn["expect"].(map[string]any)
		delete(expect, "output_contains_any")
	})
	code, violations := runLintArgs(t, "--case", caseDir, "--vocab", DefaultVocab(),
		"--canary-prefix", distillCanaryPrefix)
	if code != 1 {
		t.Errorf("exit code = %d, want 1", code)
	}
	if !hasRule(violations, "expect.smalltalk") {
		t.Errorf("no expect.smalltalk violation: %v", violations)
	}
}

// §4.1 regression: without --canary-prefix the workbank tree still lints clean
// under the default WORKBANK-CANARY rule.
func TestLintWorkbankDefaultCanaryClean(t *testing.T) {
	casesRoot := filepath.Join(lab.RepoRoot(), "bench", "workbank", "cases")
	if _, err := os.Stat(casesRoot); err != nil {
		t.Skip("workbank cases not present")
	}
	code, violations := runLintArgs(t, "--cases", casesRoot, "--vocab", DefaultVocab())
	if code != 0 || len(violations) != 0 {
		t.Errorf("workbank lint: exit code = %d, %d violation(s): %v", code, len(violations), violations)
	}
}
