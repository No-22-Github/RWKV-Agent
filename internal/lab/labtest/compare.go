// Package labtest implements the comparison rules from
// docs/go-tooling-migration.md §4.3 and the plumbing to run a migrated
// command against a recorded baseline.
//
// It exists because "the port is correct" is not a claim anyone can eyeball:
// every command's output is diffed against the output of the Python original
// on the same input, under rules that are strict where the bytes matter
// (training corpora, bank hashes) and relaxed where Python and Go legitimately
// differ (JSON key order, int-vs-float spelling).
package labtest

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// BaselineDir is where M0 recorded the Python tools' output. runs/ is
// gitignored, so this tree only exists on the machine doing the migration.
func BaselineDir() string {
	return filepath.Join(lab.RepoRoot(), "runs", "migration-baseline")
}

// HaveBaseline reports whether a named baseline was recorded.
func HaveBaseline(name string) bool {
	_, err := os.Stat(filepath.Join(BaselineDir(), name, "stdout.txt"))
	return err == nil
}

// Baseline reads one recorded stream ("stdout.txt" / "stderr.txt") and exit code.
func Baseline(name, stream string) ([]byte, int, error) {
	dir := filepath.Join(BaselineDir(), name)
	data, err := os.ReadFile(filepath.Join(dir, stream))
	if err != nil {
		return nil, 0, err
	}
	codeBytes, err := os.ReadFile(filepath.Join(dir, "exit.txt"))
	if err != nil {
		return nil, 0, err
	}
	var code int
	if _, err := fmt.Sscanf(strings.TrimSpace(string(codeBytes)), "%d", &code); err != nil {
		return nil, 0, err
	}
	return data, code, nil
}

// CompareText is the strict rule: text output must match byte for byte.
// The only tolerated difference is a program name at the start of a line,
// which §4.2 allows (paths:, tracecorpus:).
func CompareText(got, want []byte) error {
	if string(got) == string(want) {
		return nil
	}
	return fmt.Errorf("text differs\n--- got ---\n%s\n--- want ---\n%s", got, want)
}

// CompareJSON is the JSON rule: parse both sides and compare deeply, with
// numbers compared by value (Python's 1.0 and Go's 1 are equal) and strings
// compared byte for byte. Key order is not significant.
func CompareJSON(got, want []byte) error {
	var g, w any
	if err := decode(got, &g); err != nil {
		return fmt.Errorf("got is not valid JSON: %w", err)
	}
	if err := decode(want, &w); err != nil {
		return fmt.Errorf("want is not valid JSON: %w", err)
	}
	if diff := diffJSON(g, w, "$"); diff != "" {
		return fmt.Errorf("JSON differs: %s", diff)
	}
	return nil
}

// CompareJSONL applies the JSON rule line by line. Both sides are split with
// Python's line-boundary rules, and trailing blank lines are ignored the way
// the originals' print loops produce them.
func CompareJSONL(got, want []byte) error {
	gl := nonEmptyLines(got)
	wl := nonEmptyLines(want)
	if len(gl) != len(wl) {
		return fmt.Errorf("line count differs: got %d, want %d", len(gl), len(wl))
	}
	for i := range gl {
		var g, w any
		if err := decode([]byte(gl[i]), &g); err != nil {
			return fmt.Errorf("got line %d is not valid JSON: %w", i+1, err)
		}
		if err := decode([]byte(wl[i]), &w); err != nil {
			return fmt.Errorf("want line %d is not valid JSON: %w", i+1, err)
		}
		if diff := diffJSON(g, w, fmt.Sprintf("$[%d]", i+1)); diff != "" {
			return fmt.Errorf("JSONL line %d differs: %s", i+1, diff)
		}
	}
	return nil
}

// CompareBytes is the strictest rule, for the artifacts whose exact bytes are
// load-bearing: the bank file (bank_version is its sha256) and rows.jsonl.
func CompareBytes(got, want []byte) error {
	if len(got) != len(want) {
		return fmt.Errorf("byte length differs: got %d, want %d", len(got), len(want))
	}
	for i := range got {
		if got[i] != want[i] {
			lo := i - 40
			if lo < 0 {
				lo = 0
			}
			hi := i + 40
			if hi > len(got) {
				hi = len(got)
			}
			return fmt.Errorf("first byte difference at offset %d\n got: %q\nwant: %q", i, got[lo:hi], want[lo:hi])
		}
	}
	return nil
}

func decode(data []byte, out *any) error {
	v, err := lab.DecodeJSON(strings.NewReader(string(data)))
	if err != nil {
		return err
	}
	*out = v
	return nil
}

func nonEmptyLines(data []byte) []string {
	var out []string
	for _, line := range lab.SplitLines(string(data)) {
		if strings.TrimSpace(line) != "" {
			out = append(out, line)
		}
	}
	return out
}

func diffJSON(g, w any, path string) string {
	switch gv := g.(type) {
	case map[string]any:
		wv, ok := w.(map[string]any)
		if !ok {
			return fmt.Sprintf("%s: type differs (object vs %T)", path, w)
		}
		for k := range gv {
			if _, ok := wv[k]; !ok {
				return fmt.Sprintf("%s.%s: present in got, missing in want", path, k)
			}
		}
		for k := range wv {
			if _, ok := gv[k]; !ok {
				return fmt.Sprintf("%s.%s: missing in got, present in want", path, k)
			}
		}
		for _, k := range sortedKeys(gv) {
			if d := diffJSON(gv[k], wv[k], path+"."+k); d != "" {
				return d
			}
		}
		return ""
	case []any:
		wv, ok := w.([]any)
		if !ok {
			return fmt.Sprintf("%s: type differs (array vs %T)", path, w)
		}
		if len(gv) != len(wv) {
			return fmt.Sprintf("%s: length differs (got %d, want %d)", path, len(gv), len(wv))
		}
		for i := range gv {
			if d := diffJSON(gv[i], wv[i], fmt.Sprintf("%s[%d]", path, i)); d != "" {
				return d
			}
		}
		return ""
	case string:
		wv, ok := w.(string)
		if !ok || gv != wv {
			return fmt.Sprintf("%s: string differs (got %q, want %v)", path, gv, w)
		}
		return ""
	case bool:
		wv, ok := w.(bool)
		if !ok || gv != wv {
			return fmt.Sprintf("%s: bool differs (got %v, want %v)", path, gv, w)
		}
		return ""
	case nil:
		if w != nil {
			return fmt.Sprintf("%s: got null, want %v", path, w)
		}
		return ""
	default:
		gn, gok := asFloat(g)
		wn, wok := asFloat(w)
		if !gok || !wok {
			return fmt.Sprintf("%s: uncomparable values (got %T, want %T)", path, g, w)
		}
		if math.IsNaN(gn) || math.IsNaN(wn) {
			return fmt.Sprintf("%s: NaN compared", path)
		}
		if gn != wn {
			return fmt.Sprintf("%s: number differs (got %v, want %v)", path, gn, wn)
		}
		return ""
	}
}

func asFloat(v any) (float64, bool) {
	switch n := v.(type) {
	case json.Number:
		f, err := n.Float64()
		if err != nil {
			return 0, false
		}
		return f, true
	case float64:
		return n, true
	case int:
		return float64(n), true
	}
	return 0, false
}

func sortedKeys(m map[string]any) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	for i := 1; i < len(keys); i++ {
		for j := i; j > 0 && keys[j] < keys[j-1]; j-- {
			keys[j], keys[j-1] = keys[j-1], keys[j]
		}
	}
	return keys
}

// RunCLI executes the built rwkv-lab binary with args in the repository root.
// It is what the migration comparisons use to produce the "got" side.
func RunCLI(args ...string) (stdout, stderr []byte, code int, err error) {
	root := lab.RepoRoot()
	bin := filepath.Join(root, "bin", "rwkv-lab")
	if _, statErr := os.Stat(bin); statErr != nil {
		return nil, nil, 0, fmt.Errorf("bin/rwkv-lab not built: go build -o bin/rwkv-lab ./cmd/rwkv-lab")
	}
	cmd := exec.Command(bin, args...)
	cmd.Dir = root
	var out, errBuf strings.Builder
	cmd.Stdout = &out
	cmd.Stderr = &errBuf
	runErr := cmd.Run()
	code = 0
	if exitErr, ok := runErr.(*exec.ExitError); ok {
		code = exitErr.ExitCode()
	} else if runErr != nil {
		return nil, nil, 0, runErr
	}
	return []byte(out.String()), []byte(errBuf.String()), code, nil
}
