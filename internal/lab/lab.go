// Package lab holds helpers shared by the rwkv-lab development tools.
//
// The tools are a straight port of the Python scripts they replace, and the
// migration contract is that they produce the same bytes as the originals
// (docs/go-tooling-migration.md §4.3). Most of what lives here exists for that
// reason: Python's json module, str.splitlines and round() do not have direct
// Go equivalents, and the differences are exactly where a silent port bug
// would hide.
package lab

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"unicode/utf8"
)

// DecodeJSON parses JSON the way Python's json.loads does for our purposes:
// numbers keep their source literal (json.Number) so that re-encoding writes
// `9000.0` rather than Go's `9000`. Python distinguishes int from float and
// the bank file's bytes depend on that (see build.py's bank_version).
func DecodeJSON(r io.Reader) (any, error) {
	dec := json.NewDecoder(r)
	dec.UseNumber()
	var v any
	if err := dec.Decode(&v); err != nil {
		return nil, err
	}
	return v, nil
}

// DecodeJSONBytes is DecodeJSON over a byte slice.
func DecodeJSONBytes(data []byte) (any, error) {
	return DecodeJSON(bytes.NewReader(data))
}

// OrderedObjectKeys returns the keys of the object at top-level key of a JSON
// document, in source order. Go maps do not preserve object order, but Python
// dicts do, and some of the originals depend on it (coverage.py's
// largest-remainder tie-break walks level_mix in file order).
func OrderedObjectKeys(data []byte, key string) ([]string, error) {
	var top map[string]json.RawMessage
	if err := json.Unmarshal(data, &top); err != nil {
		return nil, err
	}
	raw, ok := top[key]
	if !ok {
		return nil, fmt.Errorf("no top-level key %q", key)
	}
	dec := json.NewDecoder(bytes.NewReader(raw))
	dec.UseNumber()
	tok, err := dec.Token()
	if err != nil {
		return nil, err
	}
	if delim, ok := tok.(json.Delim); !ok || delim != '{' {
		return nil, fmt.Errorf("%q is not a JSON object", key)
	}
	var keys []string
	for dec.More() {
		tok, err := dec.Token()
		if err != nil {
			return nil, err
		}
		name, ok := tok.(string)
		if !ok {
			return nil, fmt.Errorf("%q has a non-string key", key)
		}
		keys = append(keys, name)
		var skip any
		if err := dec.Decode(&skip); err != nil {
			return nil, err
		}
	}
	return keys, nil
}

// DecodeJSONFile is DecodeJSON over a file path.
func DecodeJSONFile(path string) (any, error) {
	fh, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer fh.Close()
	return DecodeJSON(fh)
}

// EncodeJSON marshals v with Python's json.dumps(ensure_ascii=False) escaping
// rules. Go escapes <, > and & by default; Python does not, and those
// characters end up inside <tool_call> text that goes straight into training
// corpora (P2). U+2028/U+2029 are still escaped because encoding/json always
// does; the corpus has none, and P2 says to record rather than work around it.
//
// indent is the number of spaces per level, 0 for compact output. Python's
// separators=(",", ":") for compact and its default item separator for indent
// are both what encoding/json produces, so no custom writer is needed.
func EncodeJSON(v any, indent int) ([]byte, error) {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	enc.SetEscapeHTML(false)
	if indent > 0 {
		enc.SetIndent("", strings.Repeat(" ", indent))
	}
	if err := enc.Encode(v); err != nil {
		return nil, err
	}
	// Encode always appends a newline; Python's json.dumps does not. Callers
	// that print with fmt.Println get the newline back.
	return bytes.TrimSuffix(buf.Bytes(), []byte("\n")), nil
}

// SplitLines mirrors Python's str.splitlines(): it breaks on \n, \r, \r\n and
// the other line boundaries Python recognises (\v, \f, \x1c-\x1e, \x85, and
// the Unicode separators U+2028/U+2029). strings.Split(s, "\n") does not, and
// lint and decontam both depend on the Python behaviour (P4).
//
// The trailing-newline rule matches Python: "a\n" splits to ["a"], and "" to [].
func SplitLines(s string) []string {
	var out []string
	start := 0
	for i := 0; i < len(s); {
		r, size := utf8.DecodeRuneInString(s[i:])
		if !isLineBoundary(r) {
			i += size
			continue
		}
		out = append(out, s[start:i])
		// \r\n counts as one boundary.
		if r == '\r' && i+size < len(s) && s[i+size] == '\n' {
			i += size + 1
		} else {
			i += size
		}
		start = i
	}
	if start < len(s) {
		out = append(out, s[start:])
	}
	return out
}

func isLineBoundary(r rune) bool {
	switch r {
	case '\n', '\r', '\v', '\f', 0x1c, 0x1d, 0x1e, 0x85, 0x2028, 0x2029:
		return true
	}
	return false
}

// RoundHalfEven implements Python's round(x, ndigits): round half to even, on
// the exact binary value. Go's math.Round rounds half away from zero, which
// differs on ties (P8).
//
// Formatting with strconv and parsing back is how the correctly-rounded
// decimal is obtained; math.RoundToEven on x*10^n would introduce its own
// error in the scaling multiply.
func RoundHalfEven(x float64, ndigits int) float64 {
	if math.IsNaN(x) || math.IsInf(x, 0) {
		return x
	}
	s := strconv.FormatFloat(x, 'f', ndigits, 64)
	v, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return x
	}
	return v
}

// FormatFloat mimics Python's "%.*f" for the common cases our tools use.
// strconv already rounds half to even on the exact value, same as Python.
func FormatFloat(x float64, prec int) string {
	return strconv.FormatFloat(x, 'f', prec, 64)
}

// PyFloat formats a float the way Python's repr() does, so that encoding it as
// a json.Number reproduces json.dumps' bytes: shortest round-trip digits, and
// a trailing ".0" on values that would otherwise look like integers
// (Python writes 1.0, Go's strconv writes 1).
//
// Values in [0,1] never reach Python's scientific-notation thresholds, which
// is where Go's 'g' format would start to disagree; the corpus tools only
// format scores and rates.
func PyFloat(x float64) json.Number {
	s := strconv.FormatFloat(x, 'g', -1, 64)
	if !strings.ContainsAny(s, ".eE") {
		s += ".0"
	}
	return json.Number(s)
}

// RepoRoot walks up from the working directory looking for go.mod, so the
// tools' default paths can be stated relative to the repository root rather
// than to the executable (the Python originals derived them from __file__).
func RepoRoot() string {
	dir, err := os.Getwd()
	if err != nil {
		return "."
	}
	for {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "."
		}
		dir = parent
	}
}

// WriteFileExclusive writes data to path, refusing to overwrite an existing
// file unless force is set. The old pipelines relied on this to avoid
// clobbering the previous round's artifacts (§4.1).
func WriteFileExclusive(path string, data []byte, force bool) error {
	if !force {
		if _, err := os.Stat(path); err == nil {
			return fmt.Errorf("%s already exists (use --force to overwrite)", path)
		}
	}
	if dir := filepath.Dir(path); dir != "" && dir != "." {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			return err
		}
	}
	return os.WriteFile(path, data, 0o644)
}

// ReadText reads a file as UTF-8 text.
func ReadText(path string) (string, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(b), nil
}
