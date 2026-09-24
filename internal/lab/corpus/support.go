package corpus

import (
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

var stderr = os.Stderr

// orderedCounter is collections.Counter with a remembered insertion order, so
// most_common() can break ties the way Python does: by count descending, then
// by first appearance (P6).
type orderedCounter struct {
	keys   []string
	Counts map[string]int
}

func newOrderedCounter() *orderedCounter {
	return &orderedCounter{Counts: map[string]int{}}
}

func (c *orderedCounter) Add(key string) {
	if _, seen := c.Counts[key]; !seen {
		c.keys = append(c.keys, key)
	}
	c.Counts[key]++
}

func (c *orderedCounter) Merge(other *orderedCounter) {
	if other == nil {
		return
	}
	for _, key := range other.keys {
		if _, seen := c.Counts[key]; !seen {
			c.keys = append(c.keys, key)
		}
		c.Counts[key] += other.Counts[key]
	}
}

// OrderedMap renders the counter as a JSON object in insertion order.
func (c *orderedCounter) OrderedMap() *lab.OrderedMap {
	m := lab.NewOrderedMap()
	for _, key := range c.keys {
		m.Set(key, c.Counts[key])
	}
	return m
}

type countEntry struct {
	Key   string
	Count int
}

// MostCommon is Python's Counter.most_common().
func (c *orderedCounter) MostCommon() []countEntry {
	out := make([]countEntry, 0, len(c.keys))
	for _, key := range c.keys {
		out = append(out, countEntry{Key: key, Count: c.Counts[key]})
	}
	sort.SliceStable(out, func(i, j int) bool { return out[i].Count > out[j].Count })
	return out
}

// passAtCount tallies pass@k rows. Python keys the Counter by the (passed,
// runs) tuple and sorts those tuples numerically, which a formatted "p/k"
// string would not reproduce once either number reaches two digits.
type passAtCount struct {
	order []passAtKey
	seen  map[passAtKey]int
}

type passAtKey struct {
	passed int
	runs   int
}

func newPassAtCount() *passAtCount {
	return &passAtCount{seen: map[passAtKey]int{}}
}

func (c *passAtCount) Add(passed, runs int) {
	key := passAtKey{passed, runs}
	if _, ok := c.seen[key]; !ok {
		c.order = append(c.order, key)
	}
	c.seen[key]++
}

func (c *passAtCount) Sorted() []countEntry {
	sorted := append([]passAtKey(nil), c.order...)
	sort.SliceStable(sorted, func(i, j int) bool {
		if sorted[i].passed != sorted[j].passed {
			return sorted[i].passed < sorted[j].passed
		}
		return sorted[i].runs < sorted[j].runs
	})
	out := make([]countEntry, 0, len(sorted))
	for _, key := range sorted {
		out = append(out, countEntry{
			Key:   fmt.Sprintf("%d/%d", key.passed, key.runs),
			Count: c.seen[key],
		})
	}
	return out
}

// pythonKind classifies a decoded JSON value the way Python's type() does for
// the comparisons in this package: int and float are different types even when
// equal, and bool is not a number.
func pythonKind(v any) string {
	switch t := v.(type) {
	case nil:
		return "none"
	case bool:
		return "bool"
	case string:
		return "str"
	case int, int64:
		return "int"
	case float64:
		return "float"
	case json.Number:
		if strings.ContainsAny(t.String(), ".eE") {
			return "float"
		}
		return "int"
	case []any:
		return "list"
	case *lab.OrderedMap:
		return "dict"
	}
	return "other"
}

// pythonEqual is Python's `==` restricted to values of the same type, which is
// what `value == default and type(value) is type(default)` needs.
func pythonEqual(a, b any) bool {
	if pythonKind(a) != pythonKind(b) {
		return false
	}
	switch pythonKind(a) {
	case "none":
		return true
	case "bool":
		return a.(bool) == b.(bool)
	case "str":
		return a.(string) == b.(string)
	case "int":
		ai, aok := asInt64(a)
		bi, bok := asInt64(b)
		return aok && bok && ai == bi
	case "float":
		af, aok := asFloat64(a)
		bf, bok := asFloat64(b)
		return aok && bok && af == bf
	case "list":
		al, bl := a.([]any), b.([]any)
		if len(al) != len(bl) {
			return false
		}
		for i := range al {
			if !pythonEqual(al[i], bl[i]) {
				return false
			}
		}
		return true
	case "dict":
		am, bm := a.(*lab.OrderedMap), b.(*lab.OrderedMap)
		if len(am.Keys) != len(bm.Keys) {
			return false
		}
		for _, key := range am.Keys {
			bv, ok := bm.Get(key)
			if !ok || !pythonEqual(am.Values[key], bv) {
				return false
			}
		}
		return true
	}
	return false
}

// emptyMeansAbsentValue is Python's `value in ("", {}, [])`.
func emptyMeansAbsentValue(v any) bool {
	switch t := v.(type) {
	case string:
		return t == ""
	case []any:
		return len(t) == 0
	case *lab.OrderedMap:
		return len(t.Keys) == 0
	}
	return false
}

func asInt64(v any) (int64, bool) {
	switch t := v.(type) {
	case int:
		return int64(t), true
	case int64:
		return t, true
	case json.Number:
		i, err := t.Int64()
		return i, err == nil
	}
	return 0, false
}

func asFloat64(v any) (float64, bool) {
	switch t := v.(type) {
	case float64:
		return t, true
	case int:
		return float64(t), true
	case int64:
		return float64(t), true
	case json.Number:
		f, err := t.Float64()
		return f, err == nil
	}
	return 0, false
}

// pyRepr renders a string the way Python's repr() does, for the messages that
// quote one.
func pyRepr(s string) string {
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

func intField(m *lab.OrderedMap, key string) int {
	v, _ := m.Get(key)
	if i, ok := asInt64(v); ok {
		return int(i)
	}
	return 0
}

func stringField(m *lab.OrderedMap, key string) string {
	s, _ := m.Get(key)
	out, _ := s.(string)
	return out
}
