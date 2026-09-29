package lab

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"
)

// Accessors for the map[string]any trees DecodeJSON returns. Each subcommand
// package used to carry its own byte-identical copy; they live here once.

// StringOf returns m[key] when it is a string, else "".
func StringOf(m map[string]any, key string) string {
	s, _ := m[key].(string)
	return s
}

// MapOf returns m[key] when it is an object, else nil.
func MapOf(m map[string]any, key string) map[string]any {
	out, _ := m[key].(map[string]any)
	return out
}

// MapSlice keeps the object elements of a decoded JSON array.
func MapSlice(v any) []map[string]any {
	items, _ := v.([]any)
	out := make([]map[string]any, 0, len(items))
	for _, item := range items {
		if m, ok := item.(map[string]any); ok {
			out = append(out, m)
		}
	}
	return out
}

// StringList keeps the string elements of a decoded JSON array.
func StringList(v any) []string {
	items, _ := v.([]any)
	out := make([]string, 0, len(items))
	for _, item := range items {
		if s, ok := item.(string); ok {
			out = append(out, s)
		}
	}
	return out
}

// ToAnySlice widens a string slice for storage in a JSON tree.
func ToAnySlice(items []string) []any {
	out := make([]any, len(items))
	for i, item := range items {
		out[i] = item
	}
	return out
}

// NumberValue reads a JSON number (json.Number, float64 or int) as float64.
func NumberValue(v any) (float64, bool) {
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

// IntOf reads an integral JSON number. A json.Number with a fraction or
// exponent is rejected; a float64 is truncated.
func IntOf(v any) (int, bool) {
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

// Truthy is Python's bool(x) for decoded JSON values: an empty object, array,
// string, zero or null is false, anything else is true.
func Truthy(v any) bool {
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

// PyRepr renders a string the way Python's repr() does, for messages that
// must match the Python originals byte for byte.
func PyRepr(s string) string {
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

// NewFlagSet builds a subcommand flag set with the shared usage banner.
func NewFlagSet(name, description string) *flag.FlagSet {
	fs := flag.NewFlagSet(name, flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	fs.Usage = func() {
		fmt.Fprintf(os.Stderr, "%s\n\nusage: rwkv-lab %s\n\nflags:\n", description, name)
		fs.PrintDefaults()
	}
	return fs
}

// FlagWasSet reports whether a flag appeared on the command line, which
// argparse distinguishes from a flag left at its default.
func FlagWasSet(fs *flag.FlagSet, name string) bool {
	seen := false
	fs.Visit(func(f *flag.Flag) {
		if f.Name == name {
			seen = true
		}
	})
	return seen
}

// FileExists reports whether path names an existing non-directory.
func FileExists(path string) bool {
	info, err := os.Stat(path)
	return err == nil && !info.IsDir()
}
