package lab

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"
)

// OrderedMap is a JSON object that remembers the order its keys appeared in.
//
// Go's map[string]any cannot: encoding/json sorts map keys, and Python does
// not sort dict keys unless asked. Three places in the migration need the
// original order — lint's --fix rewrites a case file in place, and the corpus
// tools re-serialise teacher tool-call arguments whose byte order lands in the
// training corpus (P1).
type OrderedMap struct {
	Keys   []string
	Values map[string]any
}

// NewOrderedMap returns an empty OrderedMap.
func NewOrderedMap() *OrderedMap {
	return &OrderedMap{Values: map[string]any{}}
}

// Get returns the value for key.
func (m *OrderedMap) Get(key string) (any, bool) {
	v, ok := m.Values[key]
	return v, ok
}

// Set inserts or replaces a key, appending it to the order if it is new.
func (m *OrderedMap) Set(key string, value any) {
	if m.Values == nil {
		m.Values = map[string]any{}
	}
	if _, ok := m.Values[key]; !ok {
		m.Keys = append(m.Keys, key)
	}
	m.Values[key] = value
}

// AsMap converts to a plain map, losing order.
func (m *OrderedMap) AsMap() map[string]any {
	if m == nil {
		return nil
	}
	out := make(map[string]any, len(m.Keys))
	for _, k := range m.Keys {
		out[k] = Plainify(m.Values[k])
	}
	return out
}

// Plainify converts OrderedMaps inside a decoded value into plain maps,
// recursively, for code that does not care about key order.
func Plainify(v any) any {
	switch t := v.(type) {
	case *OrderedMap:
		out := make(map[string]any, len(t.Keys))
		for _, k := range t.Keys {
			out[k] = Plainify(t.Values[k])
		}
		return out
	case []any:
		out := make([]any, len(t))
		for i, item := range t {
			out[i] = Plainify(item)
		}
		return out
	default:
		return v
	}
}

// DecodeOrderedJSON parses JSON into OrderedMaps, arrays and scalars. Numbers
// stay json.Number so re-encoding reproduces the source spelling.
func DecodeOrderedJSON(data []byte) (any, error) {
	dec := json.NewDecoder(bytes.NewReader(data))
	dec.UseNumber()
	v, err := decodeOrderedValue(dec)
	if err != nil {
		return nil, err
	}
	return v, nil
}

// DecodeOrderedJSONFile is DecodeOrderedJSON over a file path.
func DecodeOrderedJSONFile(path string) (any, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	return DecodeOrderedJSON(data)
}

func decodeOrderedValue(dec *json.Decoder) (any, error) {
	tok, err := dec.Token()
	if err != nil {
		return nil, err
	}
	return decodeOrderedFromToken(dec, tok)
}

func decodeOrderedFromToken(dec *json.Decoder, tok json.Token) (any, error) {
	switch t := tok.(type) {
	case json.Delim:
		switch t {
		case '{':
			m := NewOrderedMap()
			for dec.More() {
				keyTok, err := dec.Token()
				if err != nil {
					return nil, err
				}
				key, ok := keyTok.(string)
				if !ok {
					return nil, fmt.Errorf("object key is not a string")
				}
				value, err := decodeOrderedValue(dec)
				if err != nil {
					return nil, err
				}
				m.Set(key, value)
			}
			if _, err := dec.Token(); err != nil { // consume '}'
				return nil, err
			}
			return m, nil
		case '[':
			var out []any
			for dec.More() {
				value, err := decodeOrderedValue(dec)
				if err != nil {
					return nil, err
				}
				out = append(out, value)
			}
			if _, err := dec.Token(); err != nil { // consume ']'
				return nil, err
			}
			if out == nil {
				out = []any{}
			}
			return out, nil
		}
		return nil, fmt.Errorf("unexpected delimiter %v", t)
	default:
		return tok, nil
	}
}

// EncodeOptions controls EncodeOrderedJSON.
type EncodeOptions struct {
	// Indent is the number of spaces per level; 0 means compact.
	Indent int
	// SortKeys sorts object keys instead of preserving order, which is what
	// build.py's sort_keys=True does.
	SortKeys bool
	// SpacedSeparators emits Python's default ", " and ": " separators rather
	// than the compact "," and ":". Python uses them whenever indent is unset.
	SpacedSeparators bool
}

// EncodeOrderedJSON writes a decoded value back out the way Python's json
// module would, including its separators, its non-ASCII handling and its
// int-vs-float spelling.
func EncodeOrderedJSON(v any, opts EncodeOptions) ([]byte, error) {
	var buf bytes.Buffer
	if err := writeOrdered(&buf, v, opts, 0); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func writeOrdered(buf *bytes.Buffer, v any, opts EncodeOptions, depth int) error {
	switch t := v.(type) {
	case nil:
		buf.WriteString("null")
	case bool:
		if t {
			buf.WriteString("true")
		} else {
			buf.WriteString("false")
		}
	case string:
		writeJSONString(buf, t)
	case json.Number:
		buf.WriteString(t.String())
	case float64:
		buf.WriteString(PyFloat(t).String())
	case int:
		fmt.Fprintf(buf, "%d", t)
	case int64:
		fmt.Fprintf(buf, "%d", t)
	case *OrderedMap:
		return writeOrderedObject(buf, t, opts, depth)
	case map[string]any:
		keys := make([]string, 0, len(t))
		for k := range t {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		om := NewOrderedMap()
		for _, k := range keys {
			om.Set(k, t[k])
		}
		return writeOrderedObject(buf, om, opts, depth)
	case []any:
		return writeOrderedArray(buf, t, opts, depth)
	default:
		// Fall back to encoding/json for anything else (structs, etc).
		data, err := json.Marshal(v)
		if err != nil {
			return err
		}
		buf.Write(data)
		return nil
	}
	return nil
}

func writeOrderedObject(buf *bytes.Buffer, m *OrderedMap, opts EncodeOptions, depth int) error {
	keys := m.Keys
	if opts.SortKeys {
		keys = append([]string(nil), keys...)
		sort.Strings(keys)
	}
	if len(keys) == 0 {
		buf.WriteString("{}")
		return nil
	}
	buf.WriteByte('{')
	for i, key := range keys {
		if i > 0 {
			buf.WriteByte(',')
		}
		writeItemBreak(buf, opts, depth, i == 0)
		writeJSONString(buf, key)
		if opts.Indent > 0 {
			buf.WriteString(": ")
		} else if opts.SpacedSeparators {
			buf.WriteString(": ")
		} else {
			buf.WriteByte(':')
		}
		if err := writeOrdered(buf, m.Values[key], opts, depth+1); err != nil {
			return err
		}
	}
	writeCloseBreak(buf, opts, depth)
	buf.WriteByte('}')
	return nil
}

func writeOrderedArray(buf *bytes.Buffer, items []any, opts EncodeOptions, depth int) error {
	if len(items) == 0 {
		buf.WriteString("[]")
		return nil
	}
	buf.WriteByte('[')
	for i, item := range items {
		if i > 0 {
			buf.WriteByte(',')
		}
		writeItemBreak(buf, opts, depth, i == 0)
		if err := writeOrdered(buf, item, opts, depth+1); err != nil {
			return err
		}
	}
	writeCloseBreak(buf, opts, depth)
	buf.WriteByte(']')
	return nil
}

// writeItemBreak emits what separates one item from the previous one. Python
// puts the newline+indent before every item when indenting, but the ", "
// separator only *between* items, so `first` suppresses the space.
func writeItemBreak(buf *bytes.Buffer, opts EncodeOptions, depth int, first bool) {
	if opts.Indent > 0 {
		buf.WriteByte('\n')
		buf.WriteString(strings.Repeat(" ", opts.Indent*(depth+1)))
	} else if opts.SpacedSeparators && !first {
		buf.WriteByte(' ')
	}
}

func writeCloseBreak(buf *bytes.Buffer, opts EncodeOptions, depth int) {
	if opts.Indent > 0 {
		buf.WriteByte('\n')
		buf.WriteString(strings.Repeat(" ", opts.Indent*depth))
	}
}

// writeJSONString escapes exactly the characters Python's json encoder does
// with ensure_ascii=False: the quote, the backslash, and C0 controls. Non-ASCII
// is written as UTF-8.
func writeJSONString(buf *bytes.Buffer, s string) {
	buf.WriteByte('"')
	for _, r := range s {
		switch r {
		case '"':
			buf.WriteString(`\"`)
		case '\\':
			buf.WriteString(`\\`)
		case '\n':
			buf.WriteString(`\n`)
		case '\r':
			buf.WriteString(`\r`)
		case '\t':
			buf.WriteString(`\t`)
		case '\b':
			buf.WriteString(`\b`)
		case '\f':
			buf.WriteString(`\f`)
		default:
			if r < 0x20 {
				fmt.Fprintf(buf, `\u%04x`, r)
			} else {
				buf.WriteRune(r)
			}
		}
	}
	buf.WriteByte('"')
}
