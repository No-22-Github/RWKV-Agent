package bank

import (
	"context"
	"encoding/json"
	"fmt"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
	"unicode"

	"github.com/no22/RWKV-Agent/internal/lab"
)

const (
	verifyTimeout     = 10 * time.Second
	defaultTolerance  = 0.01
	verifyTempPattern = "verify_all_"
)

// extOrder prefers data files over prose when choosing what to corrupt:
// verify.py reads data, not READMEs.
var extOrder = []string{".csv", ".tsv", ".txt", ".jsonl", ".log", ".json", ".yaml", ".yml", ".md"}

var numberScanRe = regexp.MustCompile(`-?\d+(?:\.\d+)?`)

// runVerify ports verify_all.py: every case's verify.py is run against its own
// expect, then re-run against a corrupted fixture to prove it is not simply
// echoing the expectation it was written next to.
//
// The sandbox conditions are load-bearing, not decoration (P9): a temp copy of
// the case, a 10s timeout, an environment holding only PATH and HOME, and
// `python3 -I -S`. verify.py files are LLM-drafted case attachments, and this
// is the only thing standing between them and the repository or the network.
func runVerify(args []string) int {
	fs := newFlagSet("bank verify",
		"Run every case's verify.py against case.json expect, plus a sabotage test.")
	casesRoot := fs.String("cases", "", "case root directory (searched recursively for case.json), or a single case dir")
	if err := fs.Parse(args); err != nil {
		return 2
	}
	if *casesRoot == "" {
		fmt.Fprintln(os.Stderr, "error: --cases is required")
		return 2
	}

	dirs, err := findCaseFiles(*casesRoot)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: --cases %s is not a directory\n", *casesRoot)
		return 2
	}
	sort.Strings(dirs)

	results := make([]*lab.OrderedMap, 0, len(dirs))
	failed := 0
	for _, dir := range dirs {
		result := verifyCase(dir)
		if ok, _ := result.Get("ok"); ok != true {
			failed++
		}
		results = append(results, result)
	}

	report := lab.NewOrderedMap()
	report.Set("cases_root", *casesRoot)
	report.Set("total", len(results))
	report.Set("passed", len(results)-failed)
	report.Set("failed", failed)
	report.Set("results", anyMapSlice(results))

	data, err := lab.EncodeOrderedJSON(report, lab.EncodeOptions{Indent: 2})
	if err == nil {
		fmt.Println(string(data))
	}
	for _, result := range results {
		caseID, _ := result.Get("case")
		ok, _ := result.Get("ok")
		status := "FAIL"
		if ok == true {
			status = "ok"
		}
		fmt.Fprintf(os.Stderr, "%s %v\n", status, caseID)
	}
	if failed > 0 {
		return 1
	}
	return 0
}

// isSmalltalkCase reports whether the case is small talk, the task type the
// answer-contract and verify rules do not apply to.
func isSmalltalkCase(caseObj map[string]any) bool {
	taskType, _ := tagsOf(caseObj)["task_type"].(string)
	return taskType == "smalltalk"
}

// verifyCase runs the two checks for one case dir and returns its report entry.
func verifyCase(caseDir string) *lab.OrderedMap {
	casePath := filepath.Join(caseDir, "case.json")
	caseObj, err := loadCaseJSON(casePath)
	if err != nil {
		if os.IsNotExist(err) {
			return resultEntry(caseDir, false, []*lab.OrderedMap{
				check("case_json", false, map[string]any{"error": "case.json missing"})})
		}
		return resultEntry(caseDir, false, []*lab.OrderedMap{
			check("case_json", false, map[string]any{"error": "case.json unreadable: " + err.Error()})})
	}
	caseID, _ := caseObj["id"].(string)
	if caseID == "" {
		caseID = filepath.Base(caseDir)
	}
	if !fileExists(filepath.Join(caseDir, "verify.py")) {
		if isSmalltalkCase(caseObj) {
			// A smalltalk case has no independently computable answer -- its
			// expectation is a word list, not a value -- so there is nothing
			// for a verify.py to recompute (§4.3). Reported as a skip, the way
			// the sabotage test skips fixtures it cannot corrupt.
			return resultEntry(caseID, true, []*lab.OrderedMap{
				check("verify_py", true, map[string]any{"warning": "verify_skipped_smalltalk"})})
		}
		return resultEntry(caseID, false, []*lab.OrderedMap{
			check("verify_py", false, map[string]any{"error": "verify.py missing"})})
	}

	numbers, outputEquals, fileExp := caseExpectations(caseObj)
	tmp := materializeCaseDir(caseDir, caseObj, nil)
	res := runVerifyScript(tmp)
	os.RemoveAll(filepath.Dir(tmp))

	if res.error != "" || res.returnCode != 0 {
		errText := res.error
		if errText == "" {
			errText = fmt.Sprintf("exit code %d", res.returnCode)
		}
		var stderrLines []string
		for _, line := range lab.SplitLines(strings.TrimSpace(res.stderr)) {
			if strings.TrimSpace(line) != "" {
				stderrLines = append(stderrLines, line)
			}
		}
		var lastLine any
		if len(stderrLines) > 0 {
			lastLine = stderrLines[len(stderrLines)-1]
		}
		entry := check("verify_run", false, map[string]any{
			"error":  "verify.py failed: " + errText,
			"detail": lastLine,
		})
		return resultEntry(caseID, false, []*lab.OrderedMap{entry})
	}

	obj, parseErr := parseVerifyStdout(res.stdout)
	if obj == nil {
		entry := check("verify_output", false, map[string]any{
			"error": "verify.py stdout is not JSON: " + parseErr,
		})
		return resultEntry(caseID, false, []*lab.OrderedMap{entry})
	}

	var checks []*lab.OrderedMap
	runExp, _ := caseObj["expect"].(map[string]any)
	runExpect, _ := runExp["run"].(map[string]any)
	if expectedStdout, ok := runExpect["expected_stdout"]; ok && expectedStdout != nil {
		objMap, _ := obj.(map[string]any)
		if produced, present := objMap["expected_stdout"]; present {
			same := jsonEqual(produced, expectedStdout)
			word := "DIFFERS from"
			if same {
				word = "matches"
			}
			checks = append(checks, check("run_expect_match", same, map[string]any{
				"detail": "verify.py expected_stdout " + word + " expect.run.expected_stdout",
			}))
			if !same {
				return resultEntry(caseID, false, checks)
			}
		}
	}

	matched, detail := matchesExpectation(obj, numbers, outputEquals, fileExp)
	switch {
	case matched == nil:
		checks = append(checks, check("verify_shape", true, map[string]any{
			"warning": "verify_shape_unknown", "detail": detail}))
	case *matched:
		checks = append(checks, check("expect_match", true, map[string]any{"detail": detail}))
	default:
		checks = append(checks, check("expect_match", false, map[string]any{
			"error": "verify_expect_mismatch", "detail": detail}))
		return resultEntry(caseID, false, checks)
	}

	checks = append(checks, sabotageAndRerun(caseDir, caseObj, numbers, outputEquals, fileExp))
	ok := true
	for _, c := range checks {
		if v, _ := c.Get("ok"); v != true {
			ok = false
		}
	}
	return resultEntry(caseID, ok, checks)
}

func resultEntry(caseID any, ok bool, checks []*lab.OrderedMap) *lab.OrderedMap {
	m := lab.NewOrderedMap()
	m.Set("case", caseID)
	m.Set("ok", ok)
	m.Set("checks", anyMapSlice(checks))
	return m
}

// anyMapSlice widens an OrderedMap slice so the encoder walks it as an array;
// a typed slice would fall through to encoding/json and serialise the struct.
func anyMapSlice(maps []*lab.OrderedMap) []any {
	out := make([]any, len(maps))
	for i, m := range maps {
		out[i] = m
	}
	return out
}

// check builds a check entry. The extra keys are inserted in the order Python
// builds them, so the report's bytes match the original.
func check(name string, ok bool, extra map[string]any) *lab.OrderedMap {
	m := lab.NewOrderedMap()
	m.Set("check", name)
	m.Set("ok", ok)
	for _, key := range []string{"warning", "error", "detail"} {
		if v, present := extra[key]; present {
			m.Set(key, v)
		}
	}
	return m
}

type verifyResult struct {
	returnCode int
	stdout     string
	stderr     string
	error      string
}

// runVerifyScript runs verify.py under the sandbox conditions described above.
func runVerifyScript(caseDir string) verifyResult {
	ctx, cancel := context.WithTimeout(context.Background(), verifyTimeout)
	defer cancel()

	cmd := exec.CommandContext(ctx, "python3", "-I", "-S", "verify.py")
	cmd.Dir = caseDir
	cmd.Env = []string{
		"PATH=" + os.Getenv("PATH"),
		"HOME=" + os.Getenv("HOME"),
	}
	var stdout, stderr strings.Builder
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr
	err := cmd.Run()

	if ctx.Err() == context.DeadlineExceeded {
		return verifyResult{error: fmt.Sprintf("timeout after %ss", pythonFloatString(10.0))}
	}
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			return verifyResult{returnCode: exitErr.ExitCode(), stdout: stdout.String(), stderr: stderr.String()}
		}
		return verifyResult{error: err.Error()}
	}
	return verifyResult{stdout: stdout.String(), stderr: stderr.String()}
}

// pythonFloatString renders a float the way Python's %s does.
func pythonFloatString(f float64) string {
	return lab.PyFloat(f).String()
}

// parseVerifyStdout parses the whole stdout as JSON, falling back to the last
// non-empty line.
func parseVerifyStdout(stdout string) (any, string) {
	text := strings.TrimSpace(stdout)
	if text == "" {
		return nil, "empty stdout"
	}
	if v, err := lab.DecodeJSONBytes([]byte(text)); err == nil {
		return v, ""
	}
	lines := lab.SplitLines(text)
	for i := len(lines) - 1; i >= 0; i-- {
		line := strings.TrimSpace(lines[i])
		if line == "" {
			continue
		}
		if v, err := lab.DecodeJSONBytes([]byte(line)); err == nil {
			return v, ""
		}
	}
	return nil, "stdout is not JSON"
}

type expectedNumber struct {
	value     float64
	tolerance float64
}

// caseExpectations collects the expectations a verify.py output is checked
// against.
func caseExpectations(caseObj map[string]any) ([]expectedNumber, []string, map[string]any) {
	var numbers []expectedNumber
	var outputEquals []string
	for _, turn := range turnObjects(caseObj) {
		exp, _ := turn["expect"].(map[string]any)
		if val, ok := exp["expected_number"]; ok {
			if f, isNum := jsonNumberValue(val); isNum {
				tol := defaultTolerance
				if t, ok := exp["tolerance"]; ok {
					if tf, isTolNum := jsonNumberValue(t); isTolNum && tf > 0 {
						tol = tf
					}
				}
				numbers = append(numbers, expectedNumber{value: f, tolerance: tol})
			}
		}
		if oe, ok := exp["output_equals"].(string); ok {
			outputEquals = append(outputEquals, oe)
		}
		if oea, ok := exp["output_equals_any"].([]any); ok {
			for _, item := range oea {
				if s, ok := item.(string); ok {
					outputEquals = append(outputEquals, s)
				}
			}
		}
	}
	fileExp := map[string]any{}
	if caseExp, ok := caseObj["expect"].(map[string]any); ok {
		if files, ok := caseExp["files"].(map[string]any); ok {
			fileExp = files
		}
	}
	return numbers, outputEquals, fileExp
}

// jsonNumberValue is Python's isinstance(x, (int, float)) and not bool.
func jsonNumberValue(v any) (float64, bool) {
	n, ok := v.(json.Number)
	if !ok {
		return 0, false
	}
	f, err := n.Float64()
	return f, err == nil
}

func numEq(a, b, tol float64) bool {
	limit := tol
	if limit < 1e-12 {
		limit = 1e-12
	}
	return absFloat(a-b) <= limit
}

func absFloat(x float64) float64 {
	if x < 0 {
		return -x
	}
	return x
}

// matchesExpectation tries to match a parsed verify.py output against the
// case's expectations. matched is nil when the shape is not recognised, which
// is a warning rather than a failure.
func matchesExpectation(obj any, numbers []expectedNumber, outputEquals []string, fileExp map[string]any) (*bool, string) {
	objMap, ok := obj.(map[string]any)
	if !ok {
		return nil, "output is not a JSON object"
	}

	expNum, hasExpNum := objMap["expected_number"]
	if !hasExpNum || expNum == nil {
		if maybe, ok := objMap["expected"]; ok {
			if _, isNum := jsonNumberValue(maybe); isNum {
				expNum, hasExpNum = maybe, true
			}
		}
	}
	if hasExpNum && expNum != nil {
		val, isNum := jsonNumberValue(expNum)
		if !isNum {
			return boolPtr(false), fmt.Sprintf("expected_number is not numeric: %s", pyReprValue(expNum))
		}
		if len(numbers) == 0 {
			return boolPtr(false), "verify outputs a number but no turn expect has expected_number"
		}
		for _, want := range numbers {
			if numEq(val, want.value, want.tolerance) {
				return boolPtr(true), fmt.Sprintf("number %s matches expected_number %s (tol %s)",
					pyReprValue(val), pyReprValue(want.value), pythonFloatString(want.tolerance))
			}
		}
		return boolPtr(false), fmt.Sprintf("number %s matches none of expected_number %s",
			pyReprValue(val), pyReprValue(numberValues(numbers)))
	}

	if filesAny, hasFiles := objMap["files"]; hasFiles {
		files, ok := filesAny.(map[string]any)
		if !ok {
			return boolPtr(false), "verify 'files' is not an object"
		}
		var problems []string
		compared := false
		for path, expAny := range fileExp {
			exp, ok := expAny.(map[string]any)
			if !ok {
				continue
			}
			if equals, hasEquals := exp["equals"]; hasEquals {
				compared = true
				if !jsonEqual(files[path], equals) {
					problems = append(problems, path+": equals mismatch")
				}
			}
			if contains, ok := exp["contains"].([]any); ok {
				compared = true
				content, isStr := files[path].(string)
				if !isStr {
					problems = append(problems, path+": missing from verify output")
				} else {
					for _, subAny := range contains {
						sub, _ := subAny.(string)
						if !strings.Contains(content, sub) {
							problems = append(problems, fmt.Sprintf("%s: missing substring %s", path, pyReprValue(sub)))
						}
					}
				}
			}
		}
		if len(problems) > 0 {
			return boolPtr(false), strings.Join(problems, "; ")
		}
		if compared {
			return boolPtr(true), "files match expect.files"
		}
		return boolPtr(true), "files output present; expect.files has no equals/contains to compare"
	}

	sval, hasSval := objMap["expected_string"]
	if !hasSval || sval == nil {
		if s, ok := objMap["expected"].(string); ok {
			sval, hasSval = s, true
		}
	}
	if s, ok := sval.(string); ok && hasSval {
		if containsString(outputEquals, s) {
			return boolPtr(true), fmt.Sprintf("string %s matches output_equals", pyReprValue(s))
		}
		for _, want := range numbers {
			fval, err := strconv.ParseFloat(strings.TrimSpace(s), 64)
			if err != nil {
				continue
			}
			if numEq(fval, want.value, want.tolerance) {
				return boolPtr(true), fmt.Sprintf("string %s matches expected_number %s",
					pyReprValue(s), pyReprValue(want.value))
			}
		}
		return boolPtr(false), fmt.Sprintf("string %s matches neither output_equals %s nor expected_number %s",
			pyReprValue(s), pyReprValue(outputEquals), pyReprValue(numberValues(numbers)))
	}

	return nil, fmt.Sprintf("unrecognized verify output shape (keys: %s)", pyReprValue(sortedMapKeys(objMap)))
}

func numberValues(numbers []expectedNumber) []any {
	out := make([]any, 0, len(numbers))
	for _, n := range numbers {
		out = append(out, n.value)
	}
	return out
}

func boolPtr(b bool) *bool { return &b }

func sortedMapKeys(m map[string]any) []any {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	out := make([]any, len(keys))
	for i, k := range keys {
		out[i] = k
	}
	return out
}

// jsonEqual is a Python-style == between two decoded JSON values, where 1 and
// 1.0 are equal and booleans are not numbers.
func jsonEqual(a, b any) bool {
	if af, aok := jsonNumberValue(a); aok {
		if bf, bok := jsonNumberValue(b); bok {
			return af == bf
		}
		return false
	}
	switch at := a.(type) {
	case nil:
		return b == nil
	case string:
		bs, ok := b.(string)
		return ok && at == bs
	case bool:
		bb, ok := b.(bool)
		return ok && at == bb
	case []any:
		bs, ok := b.([]any)
		if !ok || len(at) != len(bs) {
			return false
		}
		for i := range at {
			if !jsonEqual(at[i], bs[i]) {
				return false
			}
		}
		return true
	case map[string]any:
		bm, ok := b.(map[string]any)
		if !ok || len(at) != len(bm) {
			return false
		}
		for k, v := range at {
			bv, present := bm[k]
			if !present || !jsonEqual(v, bv) {
				return false
			}
		}
		return true
	}
	return false
}

func extRank(name string) int {
	lower := strings.ToLower(name)
	for i, ext := range extOrder {
		if strings.HasSuffix(lower, ext) {
			return i
		}
	}
	return len(extOrder)
}

// materializeCaseDir copies a case dir to a temp dir and writes case.json's
// files to disk, because case fixtures live inside case.json (schema v5) and
// verify.py reads them from its working directory. filesOverride replaces
// specific paths for the sabotage run.
func materializeCaseDir(caseDir string, caseObj map[string]any, filesOverride map[string]string) string {
	parent, err := os.MkdirTemp("", verifyTempPattern)
	if err != nil {
		return ""
	}
	tmp := filepath.Join(parent, filepath.Base(caseDir))
	copyTree(caseDir, tmp)

	files := anyMap(caseObj["files"])
	for rel, content := range files {
		text := pyStrValue(content)
		if override, ok := filesOverride[rel]; ok {
			text = override
		}
		target := filepath.Join(tmp, rel)
		os.MkdirAll(filepath.Dir(target), 0o755)
		os.WriteFile(target, []byte(text), 0o644)
	}

	if len(filesOverride) > 0 {
		// The bank contract lets verify.py read fixtures either from case.json
		// or from its working directory; the sabotage must be visible to both
		// styles, so the copied case.json is rewritten too.
		caseCopy := filepath.Join(tmp, "case.json")
		if embedded, err := loadCaseJSON(caseCopy); err == nil {
			embeddedFiles := anyMap(embedded["files"])
			if embeddedFiles == nil {
				embeddedFiles = map[string]any{}
			}
			for rel, content := range filesOverride {
				embeddedFiles[rel] = content
			}
			embedded["files"] = embeddedFiles
			if data, err := lab.EncodeJSON(embedded, 0); err == nil {
				os.WriteFile(caseCopy, data, 0o644)
			}
		}
	}
	return tmp
}

func copyTree(src, dst string) {
	filepath.WalkDir(src, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return nil
		}
		if d.IsDir() && (d.Name() == "__pycache__" || d.Name() == ".venv") {
			return filepath.SkipDir
		}
		rel, err := filepath.Rel(src, path)
		if err != nil {
			return nil
		}
		target := filepath.Join(dst, rel)
		if d.IsDir() {
			os.MkdirAll(target, 0o755)
			return nil
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return nil
		}
		os.MkdirAll(filepath.Dir(target), 0o755)
		os.WriteFile(target, data, 0o644)
		return nil
	})
}

// sabotageAndRerun corrupts one fixture value and asserts verify.py notices.
func sabotageAndRerun(caseDir string, caseObj map[string]any, numbers []expectedNumber, outputEquals []string, fileExp map[string]any) *lab.OrderedMap {
	files := anyMap(caseObj["files"])
	if len(files) == 0 {
		return check("sabotage", true, map[string]any{
			"warning": "sabotage_skipped_no_files",
			"detail":  "case has no files to corrupt",
		})
	}
	var path, newContent, note, method string
	if len(numbers) > 0 {
		path, newContent, note = corruptNumeric(files, numbers[0].value, numbers[0].tolerance)
		method = "number+1"
	}
	if path == "" {
		path, newContent, note = corruptFirstLine(files)
		method = "delete_first_line"
	}
	if path == "" {
		return check("sabotage", true, map[string]any{
			"warning": "sabotage_skipped_no_content",
			"detail":  "no corruptable number or line found in case files",
		})
	}

	tmp := materializeCaseDir(caseDir, caseObj, map[string]string{path: newContent})
	res := runVerifyScript(tmp)
	os.RemoveAll(filepath.Dir(tmp))

	label := fmt.Sprintf("%s on %s (%s)", method, path, note)
	if res.error != "" || res.returnCode != 0 {
		return check("sabotage", true, map[string]any{
			"detail": label + "; verify.py failed after sabotage (detected)"})
	}
	obj, _ := parseVerifyStdout(res.stdout)
	if obj == nil {
		return check("sabotage", true, map[string]any{
			"detail": label + "; verify output unparseable after sabotage (detected)"})
	}
	matched, mdetail := matchesExpectation(obj, numbers, outputEquals, fileExp)
	if matched != nil && *matched {
		return check("sabotage", false, map[string]any{
			"error":  "sabotage_undetected",
			"detail": label + " but verify.py still matches expect: " + mdetail,
		})
	}
	return check("sabotage", true, map[string]any{
		"detail": label + "; output diverged: " + mdetail})
}

// corruptNumeric increments the first number (across files) that is numerically
// equal to expected.
func corruptNumeric(files map[string]any, expected, tol float64) (string, string, string) {
	paths := sortedFilePaths(files)
	for _, path := range paths {
		content, ok := files[path].(string)
		if !ok || content == "" {
			continue
		}
		for _, match := range numberMatches(content) {
			val, err := strconv.ParseFloat(match.text, 64)
			if err != nil {
				continue
			}
			limit := tol
			if limit < 1e-9 {
				limit = 1e-9
			}
			if absFloat(val-expected) > limit {
				continue
			}
			newVal := val + 1.0
			newText := ""
			if !strings.Contains(match.text, ".") && newVal == float64(int64(newVal)) {
				newText = strconv.FormatInt(int64(newVal), 10)
			} else {
				newText = pythonFloatString(newVal)
			}
			corrupted := content[:match.start] + newText + content[match.end:]
			return path, corrupted, fmt.Sprintf("%s -> %s", match.text, newText)
		}
	}
	return "", "", ""
}

// corruptFirstLine deletes the first non-empty line of the first CSV/text file
// that has one.
func corruptFirstLine(files map[string]any) (string, string, string) {
	for _, path := range sortedFilePaths(files) {
		content, ok := files[path].(string)
		if !ok || content == "" {
			continue
		}
		lines := strings.Split(content, "\n")
		for i, line := range lines {
			if strings.TrimSpace(line) != "" {
				lines = append(lines[:i], lines[i+1:]...)
				return path, strings.Join(lines, "\n"), "deleted first non-empty line"
			}
		}
	}
	return "", "", ""
}

func sortedFilePaths(files map[string]any) []string {
	paths := make([]string, 0, len(files))
	for path := range files {
		paths = append(paths, path)
	}
	sort.SliceStable(paths, func(i, j int) bool {
		ri, rj := extRank(filepath.Base(paths[i])), extRank(filepath.Base(paths[j]))
		if ri != rj {
			return ri < rj
		}
		return paths[i] < paths[j]
	})
	return paths
}

type numberMatch struct {
	start int
	end   int
	text  string
}

// numberMatches is NUMBER_RE with its lookarounds applied by hand: Go's regexp
// has no lookbehind, and the boundary rule (no word character or dot on either
// side) is what keeps "v1.2.3" from yielding a number.
func numberMatches(content string) []numberMatch {
	var out []numberMatch
	for _, loc := range numberScanRe.FindAllStringIndex(content, -1) {
		start, end := loc[0], loc[1]
		if start > 0 && isWordOrDot(runeAtBefore(content, start)) {
			continue
		}
		if end < len(content) && isWordOrDot(runeAt(content, end)) {
			continue
		}
		out = append(out, numberMatch{start: start, end: end, text: content[start:end]})
	}
	return out
}

func isWordOrDot(r rune) bool {
	return r == '.' || r == '_' || unicode.IsLetter(r) || unicode.IsNumber(r)
}

func runeAt(s string, index int) rune {
	for _, r := range s[index:] {
		return r
	}
	return 0
}

func runeAtBefore(s string, index int) rune {
	var last rune
	for _, r := range s[:index] {
		last = r
	}
	return last
}
