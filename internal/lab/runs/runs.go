// Package runs ports the run-analysis tools: wire metrics, the validity gate,
// the capability gate, the failure audit, run/config comparison, the scoring
// ledger and replica summaries.
//
// Everything here reads the artifacts an agent-eval run leaves behind
// (run.json, summary.json, trace.jsonl, experiment.json) and never re-scores a
// case: official pass/fail is read from the artifacts, and these tools only
// classify, aggregate and compare what the harness already decided.
package runs

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"unicode"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// stderr is where the tools' diagnostics go; stdout carries the payload (§4.2).
var stderr = os.Stderr

// DefaultLedgerCases is the per-case ledger, relative to the repository root.
func DefaultLedgerCases() string {
	return filepath.Join(lab.RepoRoot(), "bench", "workbank", "ledger", "cases.jsonl")
}

// DefaultLedgerRuns is the per-run ledger.
func DefaultLedgerRuns() string {
	return filepath.Join(lab.RepoRoot(), "bench", "workbank", "ledger", "runs.jsonl")
}

// statPath reports whether path is a directory.
func statPath(path string) (bool, error) {
	info, err := os.Stat(path)
	if err != nil {
		return false, err
	}
	return info.IsDir(), nil
}

// InfrastructureFailure reports whether a failure string is a transport or
// provider break rather than a model or protocol score.
//
// Exported because three tools share the rule (wire, audit, replicate): a run
// whose failures are infrastructure is not a reading of the model, and all
// three have to agree on which strings count.
func InfrastructureFailure(failure string) bool {
	if !strings.HasPrefix(failure, "runner error:") {
		return false
	}
	text := strings.ToLower(failure)
	if strings.Contains(text, "agent protocol error:") {
		return false
	}
	for _, marker := range []string{
		"rwkv_lightning continuation error:", "http 4", "http 5",
		"connection refused", "context deadline exceeded", "no such host",
		"timeout", "connection reset", "unexpected eof", "broken pipe",
	} {
		if strings.Contains(text, marker) {
			return true
		}
	}
	return false
}

// LoadJSONFile reads a JSON object, returning nil when the file is absent and
// required is false.
func LoadJSONFile(path string, required bool) (map[string]any, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) && !required {
			return nil, nil
		}
		if os.IsNotExist(err) {
			return nil, fmt.Errorf("missing required file: %s", path)
		}
		return nil, err
	}
	obj, err := lab.DecodeJSONBytes(data)
	if err != nil {
		return nil, fmt.Errorf("invalid JSON in %s: %v", path, err)
	}
	m, _ := obj.(map[string]any)
	return m, nil
}

// ReadJSONL reads a JSONL file, skipping blank and unparseable lines with a
// warning the way the originals do.
func ReadJSONL(path string) []map[string]any {
	text, err := lab.ReadText(path)
	if err != nil {
		return nil
	}
	var rows []map[string]any
	for i, line := range lab.SplitLines(text) {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		obj, err := lab.DecodeJSONBytes([]byte(line))
		if err != nil {
			fmt.Fprintf(os.Stderr, "warning: %s:%d is not valid JSON, skipped\n", path, i+1)
			continue
		}
		if m, ok := obj.(map[string]any); ok {
			rows = append(rows, m)
		}
	}
	return rows
}

// AppendJSONL appends one row, sorted keys, Python's ", "/": " separators.
func AppendJSONL(path string, row map[string]any) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0o644)
	if err != nil {
		return err
	}
	defer file.Close()
	data, err := lab.EncodeOrderedJSON(row, lab.EncodeOptions{SortKeys: true, SpacedSeparators: true})
	if err != nil {
		return err
	}
	_, err = file.Write(append(data, '\n'))
	return err
}

// WriteJSONFile writes a JSON document the way Python's json.dump does with
// indent=2, plus a trailing newline.
func WriteJSONFile(path string, v any) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	data, err := lab.EncodeJSON(v, 2)
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(data, '\n'), 0o644)
}

// --- small JSON helpers -----------------------------------------------------

func stringOf(m map[string]any, key string) string {
	s, _ := m[key].(string)
	return s
}

func mapOf(m map[string]any, key string) map[string]any {
	out, _ := m[key].(map[string]any)
	return out
}

func sliceOf(m map[string]any, key string) []any {
	out, _ := m[key].([]any)
	return out
}

func mapSlice(v any) []map[string]any {
	items, _ := v.([]any)
	out := make([]map[string]any, 0, len(items))
	for _, item := range items {
		if m, ok := item.(map[string]any); ok {
			out = append(out, m)
		}
	}
	return out
}

// isNumber is Python's isinstance(x, (int, float)) and not isinstance(x, bool).
func isNumber(v any) bool {
	if _, isBool := v.(bool); isBool {
		return false
	}
	_, ok := numberValue(v)
	return ok
}

func numberValue(v any) (float64, bool) {
	switch t := v.(type) {
	case json.Number:
		f, err := t.Float64()
		return f, err == nil
	case float64:
		return t, true
	case int:
		return float64(t), true
	}
	return 0, false
}

func intOf(v any) (int, bool) {
	switch t := v.(type) {
	case json.Number:
		i, err := t.Int64()
		if err != nil {
			return 0, false
		}
		return int(i), true
	case int:
		return t, true
	case float64:
		return int(t), true
	}
	return 0, false
}

func truthy(v any) bool {
	switch t := v.(type) {
	case nil:
		return false
	case bool:
		return t
	case string:
		return t != ""
	case json.Number:
		f, err := t.Float64()
		return err != nil || f != 0
	case []any:
		return len(t) > 0
	case map[string]any:
		return len(t) > 0
	}
	return true
}

// pyQuote is Python's repr() for a string.
func pyQuote(s string) string {
	quote := byte('\'')
	if strings.Contains(s, "'") && !strings.Contains(s, `"`) {
		quote = '"'
	}
	var b strings.Builder
	b.WriteByte(quote)
	for _, r := range s {
		switch r {
		case '\\':
			b.WriteString(`\\`)
		case '\n':
			b.WriteString(`\n`)
		case '\r':
			b.WriteString(`\r`)
		case '\t':
			b.WriteString(`\t`)
		default:
			if r == rune(quote) {
				b.WriteByte('\\')
				b.WriteRune(r)
			} else if r < 0x20 || r == 0x7f {
				fmt.Fprintf(&b, `\x%02x`, r)
			} else {
				b.WriteRune(r)
			}
		}
	}
	b.WriteByte(quote)
	return b.String()
}

// labPyFloat renders a float the way Python's repr() does.
func labPyFloat(f float64) string { return lab.PyFloat(f).String() }

// isWordRune is Python's \w for str patterns (letters, digits, underscore,
// and the numeric categories), which Go's \w does not cover outside ASCII.
func isWordRune(r rune) bool {
	return r == '_' || unicode.IsLetter(r) || unicode.IsNumber(r)
}

func runeBefore(s string, index int) (rune, bool) {
	if index <= 0 {
		return 0, false
	}
	var last rune
	for _, r := range s[:index] {
		last = r
	}
	return last, true
}

func runeAt(s string, index int) (rune, bool) {
	if index >= len(s) {
		return 0, false
	}
	for _, r := range s[index:] {
		return r, true
	}
	return 0, false
}
