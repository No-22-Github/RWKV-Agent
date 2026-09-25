package corpus

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// packTestWire is the g1k wire hash, so fixtures look like real rows.
const packTestWire = "707c67403b1b2e5269ddfcd8ecee2bfb7ce4d8133912d102bc67f1324f8018cb"

func packTestMeta(caseID string, turn int, wireHash string) *lab.OrderedMap {
	return om("case_id", caseID, "turn", turn, "wire_hash", wireHash,
		"passed", true, "harness_version", "rwkv-agent-eval-v21")
}

// packTestLine renders one rows.jsonl line. Spans are the caller's business
// because the zero-call tally reads them.
func packTestLine(t *testing.T, text string, spans any, meta *lab.OrderedMap) string {
	t.Helper()
	row := lab.NewOrderedMap()
	row.Set("text", text)
	row.Set("loss_spans", spans)
	row.Set("meta", meta)
	data, err := lab.EncodeOrderedJSON(row, lab.EncodeOptions{SpacedSeparators: true})
	if err != nil {
		t.Fatal(err)
	}
	return string(data)
}

func writePackFile(t *testing.T, path string, lines ...string) {
	t.Helper()
	if err := os.WriteFile(path, []byte(strings.Join(lines, "\n")+"\n"), 0o644); err != nil {
		t.Fatal(err)
	}
}

func readPackFile(t *testing.T, path string) string {
	t.Helper()
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	return string(data)
}

func packFileSHA(t *testing.T, path string) string {
	t.Helper()
	sum := sha256.Sum256([]byte(readPackFile(t, path)))
	return hex.EncodeToString(sum[:])
}

func readPackManifest(t *testing.T, path string) map[string]any {
	t.Helper()
	var manifest map[string]any
	if err := json.Unmarshal([]byte(readPackFile(t, path)), &manifest); err != nil {
		t.Fatal(err)
	}
	return manifest
}

// capturePackRun runs fn with both streams captured. stderr is the package
// variable the commands write errors to, not os.Stderr.
func capturePackRun(t *testing.T, fn func() int) (stdout, stderrText string, code int) {
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

func packMustNotExist(t *testing.T, path string) {
	t.Helper()
	if _, err := os.Stat(path); !os.IsNotExist(err) {
		t.Fatalf("pack produced %s despite failing (stat err = %v)", path, err)
	}
}

// A dry run prints the full summary and writes nothing at all.
func TestPackDryRunPrintsStatsWithoutWriting(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	toolText := "Réponse: é\n<tool_call>{\"name\":\"calculator\"}</tool_call>"
	finalText := "The answer is 4."
	metaTool := packTestMeta("tab-5001--p1", 1, packTestWire)
	metaTool.Set("kind", "local")
	metaTool.Set("source", "base700")
	metaFinal := packTestMeta("docs-5001--p1", 2, packTestWire)
	metaFinal.Set("kind", "direct")
	metaFinal.Set("source", "distill-b01")
	metaPlain := packTestMeta("tab-5002--p1", 1, packTestWire)
	metaPlain.Set("kind", "direct")
	metaPlain.Set("source", "distill-b01")
	writePackFile(t, rowsPath,
		packTestLine(t, toolText, []any{[]any{0, len([]rune(toolText))}}, metaTool),
		packTestLine(t, finalText, []any{[]any{0, len([]rune(finalText))}}, metaFinal),
		packTestLine(t, "plain row", nil, metaPlain),
	)

	stdout, stderrText, code := capturePackRun(t, func() int {
		return runPackCmd([]string{"--rows", rowsPath, "--dry-run"})
	})
	if code != 0 {
		t.Fatalf("pack --dry-run = %d, want 0\nstderr: %s", code, stderrText)
	}
	for _, want := range []string{
		"pack: 3 rows read, 0 excluded, 3 to pack",
		"by scenario:", "  2  tab", "  1  docs",
		"by turn:", "  2  1", "  1  2",
		"2/3 (66.7%) rows have no <tool_call>",
		"tokens: p50=", "by kind:", "  2  direct", "  1  local",
		"by source:", "  2  distill-b01", "  1  base700",
		"pack: dry run, nothing written",
	} {
		if !strings.Contains(stdout, want) {
			t.Errorf("dry-run stdout misses %q\n---\n%s", want, stdout)
		}
	}
	entries, err := os.ReadDir(dir)
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) != 1 || entries[0].Name() != "rows.jsonl" {
		t.Fatalf("dry run wrote files: %v", entries)
	}
}

// A real run writes train.jsonl ({"text"} only), the accepted rows byte for
// byte, and a complete manifest; a second run into the same directory refuses.
func TestPackWritesProductsAndManifest(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	callText := "<tool_call>{\"name\":\"calculator\"}</tool_call>"
	plainText := "Just an answer."
	callLine := packTestLine(t, callText, []any{[]any{0, len([]rune(callText))}},
		packTestMeta("tab-5001--p1", 1, packTestWire))
	plainLine := packTestLine(t, plainText, nil,
		packTestMeta("tab-5002--p1", 1, packTestWire))
	writePackFile(t, rowsPath, callLine, plainLine)

	out := filepath.Join(dir, "dataset-20260925")
	stdout, stderrText, code := capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{rowsPath}, Out: out, MaxTokens: 4096})
	})
	if code != 0 {
		t.Fatalf("pack = %d, want 0\nstderr: %s", code, stderrText)
	}
	if !strings.Contains(stdout, "pack: 2 rows read, 0 excluded, 2 to pack") {
		t.Errorf("stats missing from stdout:\n%s", stdout)
	}
	if !strings.Contains(stdout, "pack: wrote train.jsonl, rows.jsonl and manifest.json to "+out) {
		t.Errorf("write confirmation missing from stdout:\n%s", stdout)
	}

	trainLines := strings.Split(strings.TrimSuffix(readPackFile(t, filepath.Join(out, "train.jsonl")), "\n"), "\n")
	if len(trainLines) != 2 {
		t.Fatalf("train.jsonl has %d lines, want 2", len(trainLines))
	}
	for index, want := range []string{callText, plainText} {
		var line map[string]any
		if err := json.Unmarshal([]byte(trainLines[index]), &line); err != nil {
			t.Fatal(err)
		}
		if len(line) != 1 {
			t.Fatalf("train line %d has keys %v, want only text", index, line)
		}
		if line["text"] != want {
			t.Fatalf("train line %d text = %q, want %q", index, line["text"], want)
		}
	}

	if got, want := readPackFile(t, filepath.Join(out, "rows.jsonl")), callLine+"\n"+plainLine+"\n"; got != want {
		t.Fatalf("rows.jsonl is not the verbatim accepted input:\ngot  %q\nwant %q", got, want)
	}

	manifest := readPackManifest(t, filepath.Join(out, "manifest.json"))
	inputs, ok := manifest["inputs"].([]any)
	if !ok || len(inputs) != 1 {
		t.Fatalf("manifest inputs = %v", manifest["inputs"])
	}
	input := inputs[0].(map[string]any)
	if input["path"] != rowsPath {
		t.Errorf("input path = %v, want %s", input["path"], rowsPath)
	}
	if input["sha256"] != packFileSHA(t, rowsPath) {
		t.Errorf("input sha256 = %v, want file digest", input["sha256"])
	}
	if input["rows"] != float64(2) {
		t.Errorf("input rows = %v, want 2", input["rows"])
	}
	if manifest["exclude"] != nil {
		t.Errorf("exclude = %v, want null without --exclude", manifest["exclude"])
	}
	if manifest["wire_hash"] != packTestWire {
		t.Errorf("wire_hash = %v", manifest["wire_hash"])
	}
	if manifest["harness_version"] != "rwkv-agent-eval-v21" {
		t.Errorf("harness_version = %v", manifest["harness_version"])
	}
	if manifest["rows"] != float64(2) {
		t.Errorf("manifest rows = %v, want 2", manifest["rows"])
	}
	tokens, ok := manifest["tokens"].(map[string]any)
	if !ok {
		t.Fatalf("manifest tokens = %v", manifest["tokens"])
	}
	p50, p99, max := tokens["p50"].(float64), tokens["p99"].(float64), tokens["max"].(float64)
	if !(max >= p99 && p99 >= p50 && p50 > 0) {
		t.Errorf("token summary out of order: p50=%v p99=%v max=%v", p50, p99, max)
	}
	if share := manifest["zero_call_share"].(float64); share != 0.5 {
		t.Errorf("zero_call_share = %v, want 0.5", share)
	}
	created := manifest["created_at"].(string)
	parsed, err := time.Parse(time.RFC3339, created)
	if err != nil || !strings.HasSuffix(created, "Z") || parsed.Location() != time.UTC {
		t.Errorf("created_at = %q, want RFC3339 UTC", created)
	}
}

// --exclude drops every turn of the listed case IDs and lands in the manifest.
func TestPackExcludeDropsEveryTurn(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	keptLine := packTestLine(t, "kept row", nil, packTestMeta("tab-5004--p1", 1, packTestWire))
	turnOne := packTestLine(t, "turn one", nil, packTestMeta("tab-5003--p1", 1, packTestWire))
	turnTwo := packTestLine(t, "turn two", nil, packTestMeta("tab-5003--p1", 2, packTestWire))
	writePackFile(t, rowsPath, turnOne, keptLine, turnTwo)

	excludePath := filepath.Join(dir, "exclude.jsonl")
	writePackFile(t, excludePath, `{"case_id": "tab-5003--p1", "reason": "spot check", "batch": "b01"}`)

	stdout, stderrText, code := capturePackRun(t, func() int {
		return runPackCmd([]string{"--rows", rowsPath, "--exclude", excludePath, "--dry-run"})
	})
	if code != 0 {
		t.Fatalf("dry run = %d\nstderr: %s", code, stderrText)
	}
	if !strings.Contains(stdout, "pack: 3 rows read, 2 excluded, 1 to pack") {
		t.Errorf("exclude stats wrong:\n%s", stdout)
	}
	if !strings.Contains(stdout, "  1  tab") || strings.Contains(stdout, "  2  tab") || strings.Contains(stdout, "  3  tab") {
		// Both turns of tab-5003--p1 are excluded, so tab drops from 3 to 1.
		t.Errorf("scenario tally ignored the exclusion:\n%s", stdout)
	}

	out := filepath.Join(dir, "dataset")
	if _, stderrText, code = capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{rowsPath}, Exclude: excludePath, Out: out, MaxTokens: 4096})
	}); code != 0 {
		t.Fatalf("pack = %d\nstderr: %s", code, stderrText)
	}
	if got := readPackFile(t, filepath.Join(out, "rows.jsonl")); got != keptLine+"\n" {
		t.Fatalf("rows.jsonl = %q, want only the kept row", got)
	}
	manifest := readPackManifest(t, filepath.Join(out, "manifest.json"))
	exclude, ok := manifest["exclude"].(map[string]any)
	if !ok {
		t.Fatalf("manifest exclude = %v", manifest["exclude"])
	}
	if exclude["path"] != excludePath || exclude["sha256"] != packFileSHA(t, excludePath) {
		t.Errorf("exclude entry = %v", exclude)
	}
	if exclude["removed"] != float64(2) {
		t.Errorf("exclude removed = %v, want 2 (both turns)", exclude["removed"])
	}
	if manifest["rows"] != float64(1) {
		t.Errorf("manifest rows = %v, want 1", manifest["rows"])
	}
	// inputs[].rows counts what the file contributed to the pack, so the
	// inputs sum equals manifest.rows.
	inputs := manifest["inputs"].([]any)
	if got := inputs[0].(map[string]any)["rows"]; got != float64(1) {
		t.Errorf("input rows = %v, want 1 after exclusion", got)
	}
}

// Gate 1: two wire hashes in one pack.
func TestPackGateMixedWireHashFailsWithoutWriting(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	writePackFile(t, rowsPath,
		packTestLine(t, "first row", nil, packTestMeta("tab-5001--p1", 1, packTestWire)),
		packTestLine(t, "second row", nil, packTestMeta("tab-5002--p1", 1, "0000000000000000000000000000000000000000000000000000000000000000")),
	)
	out := filepath.Join(dir, "dataset")
	_, stderrText, code := capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{rowsPath}, Out: out, MaxTokens: 4096})
	})
	if code != 1 {
		t.Fatalf("mixed wire_hash = %d, want 1\nstdout/stderr: %s", code, stderrText)
	}
	if !strings.Contains(stderrText, "wire_hash gate") || !strings.Contains(stderrText, "2 distinct values") {
		t.Errorf("stderr does not name the wire_hash gate: %s", stderrText)
	}
	packMustNotExist(t, out)
}

// Gate 2: a row over the token budget.
func TestPackGateOverMaxTokensFailsWithoutWriting(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	writePackFile(t, rowsPath,
		packTestLine(t, "a very long sentence that is certainly more than one token", nil,
			packTestMeta("tab-5001--p1", 1, packTestWire)),
	)
	out := filepath.Join(dir, "dataset")
	_, stderrText, code := capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{rowsPath}, Out: out, MaxTokens: 1})
	})
	if code != 1 {
		t.Fatalf("over --max-tokens = %d, want 1\nstderr: %s", code, stderrText)
	}
	if !strings.Contains(stderrText, "max-tokens gate") || !strings.Contains(stderrText, "exceed 1 tokens") {
		t.Errorf("stderr does not name the token gate: %s", stderrText)
	}
	packMustNotExist(t, out)
}

// Gate 3: either canary in model-visible text.
func TestPackGateCanaryFailsWithoutWriting(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	writePackFile(t, rowsPath,
		packTestLine(t, "prompt with DISTILL-CANARY-0011aabb inside", nil,
			packTestMeta("tab-5001--p1", 1, packTestWire)),
		packTestLine(t, "prompt with WORKBANK-CANARY-99ffeedd inside", nil,
			packTestMeta("tab-5002--p1", 1, packTestWire)),
	)
	out := filepath.Join(dir, "dataset")
	_, stderrText, code := capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{rowsPath}, Out: out, MaxTokens: 4096})
	})
	if code != 1 {
		t.Fatalf("canary rows = %d, want 1\nstderr: %s", code, stderrText)
	}
	for _, want := range []string{
		"canary gate: 1 rows contain DISTILL-CANARY",
		"canary gate: 1 rows contain WORKBANK-CANARY",
	} {
		if !strings.Contains(stderrText, want) {
			t.Errorf("stderr misses %q: %s", want, stderrText)
		}
	}
	packMustNotExist(t, out)
}

// Gate 4: two rows with identical text (and different case IDs, so the
// exclude list cannot save them).
func TestPackGateDuplicateTextFailsWithoutWriting(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	writePackFile(t, rowsPath,
		packTestLine(t, "the same answer twice", nil, packTestMeta("tab-5001--p1", 1, packTestWire)),
		packTestLine(t, "the same answer twice", nil, packTestMeta("tab-5002--p1", 1, packTestWire)),
	)
	out := filepath.Join(dir, "dataset")
	_, stderrText, code := capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{rowsPath}, Out: out, MaxTokens: 4096})
	})
	if code != 1 {
		t.Fatalf("duplicate texts = %d, want 1\nstderr: %s", code, stderrText)
	}
	if !strings.Contains(stderrText, "duplicate gate: 1 rows repeat") {
		t.Errorf("stderr does not name the duplicate gate: %s", stderrText)
	}
	packMustNotExist(t, out)
}

// Multiple --rows files concatenate in command-line order and each keeps its
// own manifest entry.
func TestPackConcatenatesInputsInOrder(t *testing.T) {
	dir := t.TempDir()
	first := filepath.Join(dir, "first.jsonl")
	second := filepath.Join(dir, "second.jsonl")
	firstLine := packTestLine(t, "from the first file", nil, packTestMeta("tab-5001--p1", 1, packTestWire))
	secondLine := packTestLine(t, "from the second file", nil, packTestMeta("docs-5001--p1", 1, packTestWire))
	writePackFile(t, first, firstLine)
	writePackFile(t, second, secondLine)

	out := filepath.Join(dir, "dataset")
	_, stderrText, code := capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{first, second}, Out: out, MaxTokens: 4096})
	})
	if code != 0 {
		t.Fatalf("pack = %d\nstderr: %s", code, stderrText)
	}
	if got := readPackFile(t, filepath.Join(out, "rows.jsonl")); got != firstLine+"\n"+secondLine+"\n" {
		t.Fatalf("rows.jsonl order = %q", got)
	}
	manifest := readPackManifest(t, filepath.Join(out, "manifest.json"))
	inputs := manifest["inputs"].([]any)
	if len(inputs) != 2 {
		t.Fatalf("manifest inputs = %v, want 2 entries", inputs)
	}
	if inputs[0].(map[string]any)["path"] != first || inputs[1].(map[string]any)["path"] != second {
		t.Errorf("manifest input order = %v", inputs)
	}
}

// --out on an existing path is refused before anything is read or written.
func TestPackRefusesExistingOutputDirectory(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	writePackFile(t, rowsPath, packTestLine(t, "row", nil, packTestMeta("tab-5001--p1", 1, packTestWire)))
	out := filepath.Join(dir, "dataset")
	if err := os.MkdirAll(out, 0o755); err != nil {
		t.Fatal(err)
	}
	marker := filepath.Join(out, "keep-me")
	if err := os.WriteFile(marker, []byte("existing"), 0o644); err != nil {
		t.Fatal(err)
	}

	_, stderrText, code := capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{rowsPath}, Out: out, MaxTokens: 4096})
	})
	if code == 0 {
		t.Fatalf("pack into an existing directory = 0, want non-zero")
	}
	if !strings.Contains(stderrText, "already exists") {
		t.Errorf("stderr = %s, want an already-exists refusal", stderrText)
	}
	entries, err := os.ReadDir(out)
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) != 1 || entries[0].Name() != "keep-me" {
		t.Fatalf("existing directory was touched: %v", entries)
	}
}

// --rows and exactly one of --out/--dry-run are required; both are usage
// errors (exit 2), not gate failures.
func TestPackFlagsRequireInputsAndOneDestination(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	writePackFile(t, rowsPath, packTestLine(t, "row", nil, packTestMeta("tab-5001--p1", 1, packTestWire)))
	cases := []struct {
		name string
		argv []string
	}{
		{"no rows", []string{"--dry-run"}},
		{"no destination", []string{"--rows", rowsPath}},
		{"both destinations", []string{"--rows", rowsPath, "--dry-run", "--out", filepath.Join(dir, "dataset")}},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			_, stderrText, code := capturePackRun(t, func() int { return runPackCmd(testCase.argv) })
			if code != 2 {
				t.Fatalf("code = %d, want 2\nstderr: %s", code, stderrText)
			}
			if !strings.Contains(stderrText, "error:") {
				t.Errorf("stderr = %s, want an error line", stderrText)
			}
		})
	}
}

// An exclude entry without case_id is a broken input, not a silent no-op.
func TestPackExcludeEntryWithoutCaseIDFails(t *testing.T) {
	dir := t.TempDir()
	rowsPath := filepath.Join(dir, "rows.jsonl")
	writePackFile(t, rowsPath, packTestLine(t, "row", nil, packTestMeta("tab-5001--p1", 1, packTestWire)))
	excludePath := filepath.Join(dir, "exclude.jsonl")
	writePackFile(t, excludePath, `{"reason": "no case id"}`)
	out := filepath.Join(dir, "dataset")
	_, stderrText, code := capturePackRun(t, func() int {
		return RunPack(PackArgs{Rows: []string{rowsPath}, Exclude: excludePath, Out: out, MaxTokens: 4096})
	})
	if code != 1 {
		t.Fatalf("exclude without case_id = %d, want 1\nstderr: %s", code, stderrText)
	}
	if !strings.Contains(stderrText, "without a case_id") {
		t.Errorf("stderr = %s", stderrText)
	}
	packMustNotExist(t, out)
}

func TestPackScenarioFallsBackToTheIDPrefix(t *testing.T) {
	cases := map[string]string{
		"tab-5001--p1":     "tab",
		"ws7-cfg-0001-a00": "ws7",
		"nodash":           "nodash",
		"":                 "",
	}
	for caseID, want := range cases {
		if got := packScenario(caseID, nil); got != want {
			t.Errorf("packScenario(%q) = %q, want %q", caseID, got, want)
		}
	}
}

// Rows rendered after §4.4 know their scenario, which the case_id prefix
// cannot say for the 700 corpus (every id starts with "ws7").
func TestPackScenarioPrefersCaseTags(t *testing.T) {
	meta := lab.NewOrderedMap()
	tags := lab.NewOrderedMap()
	tags.Set("scenario", "config")
	meta.Set("case_tags", tags)
	if got := packScenario("ws7-cfg-0001-a00", meta); got != "config" {
		t.Errorf("packScenario = %q, want config", got)
	}
}

// Nearest-rank: p50 of 4 sorted values is the 2nd, p99 the 4th.
func TestPackPercentileNearestRank(t *testing.T) {
	sorted := []int{10, 20, 30, 40}
	if got := packPercentile(sorted, 50); got != 20 {
		t.Errorf("p50 = %d, want 20", got)
	}
	if got := packPercentile(sorted, 99); got != 40 {
		t.Errorf("p99 = %d, want 40", got)
	}
	if got := packPercentile(nil, 50); got != 0 {
		t.Errorf("p50 of nothing = %d, want 0", got)
	}
}

// loss_spans are code point offsets, not byte offsets.
func TestPackCoveredTextRuneOffsets(t *testing.T) {
	text := "é中文<tool_call>{\"name\":\"x\"}</tool_call>"
	if got := packCoveredText(text, []any{[]any{0, 3}}); got != "é中文" {
		t.Errorf("rune span = %q, want é中文", got)
	}
	if got := packCoveredText(text, []any{[]any{0, 1000}}); got != text {
		t.Errorf("clamped span = %q, want the whole text", got)
	}
	spans := []any{[]any{0, 1}, "not a pair", []any{2}, []any{1, 1}}
	if got := packCoveredText(text, spans); got != "é" {
		t.Errorf("malformed spans = %q, want é", got)
	}
	if got := packCoveredText(text, nil); got != "" {
		t.Errorf("no spans = %q, want empty", got)
	}
}

func writePackTestFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

// An exclusion recorded by one batch must not strike out a later batch's rows
// for the same case: b01's bare-UNKNOWN refusal rows were excluded, the case was
// re-authored, and b02's fresh refusal rows have to survive.
func TestPackExcludeIsScopedToItsBatch(t *testing.T) {
	dir := t.TempDir()
	rows := filepath.Join(dir, "rows.jsonl")
	old := `{"text":"old refusal row","loss_spans":[[0,1]],"meta":{"case_id":"nt-5093--p1","turn":1,"wire_hash":"h","source":"distill-b01"}}`
	fresh := `{"text":"fresh refusal row","loss_spans":[[0,1]],"meta":{"case_id":"nt-5093--p1","turn":1,"wire_hash":"h","source":"distill-b02"}}`
	writePackTestFile(t, rows, old+"\n"+fresh+"\n")
	exclude := filepath.Join(dir, "exclude.jsonl")
	writePackTestFile(t, exclude, `{"case_id":"nt-5093--p1","reason":"nocap-bare-unknown","batch":"b01"}`+"\n")
	out, _, _ := capturePackRun(t, func() int {
		return runPackCmd([]string{"--rows", rows, "--exclude", exclude, "--dry-run"})
	})
	if !strings.Contains(out, "1 excluded") || !strings.Contains(out, "1 to pack") {
		t.Errorf("dry run = %q, want the b01 row excluded and the b02 row kept", out)
	}

	// A hand-written entry without a batch still drops every row of the case.
	writePackTestFile(t, exclude, `{"case_id":"nt-5093--p1","reason":"manual"}`+"\n")
	out, _, _ = capturePackRun(t, func() int {
		return runPackCmd([]string{"--rows", rows, "--exclude", exclude, "--dry-run"})
	})
	if !strings.Contains(out, "2 excluded") {
		t.Errorf("dry run = %q, want both rows excluded", out)
	}
}
