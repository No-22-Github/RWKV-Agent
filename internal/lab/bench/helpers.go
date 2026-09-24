package bench

import (
	"encoding/json"

	"github.com/no22/RWKV-Agent/internal/lab"
)

func stringOf(m map[string]any, key string) string {
	s, _ := m[key].(string)
	return s
}

func mapOfAny(m map[string]any, keys ...string) map[string]any {
	current := m
	for _, key := range keys {
		next, _ := current[key].(map[string]any)
		if next == nil {
			return nil
		}
		current = next
	}
	return current
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

func stringList(v any) []string {
	items, _ := v.([]any)
	out := make([]string, 0, len(items))
	for _, item := range items {
		if s, ok := item.(string); ok {
			out = append(out, s)
		}
	}
	return out
}

func toAnySlice(items []string) []any {
	out := make([]any, len(items))
	for i, item := range items {
		out[i] = item
	}
	return out
}

func intOfAny(v any) (int, bool) {
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

// sliceOfAny reads a key off an OrderedMap, which is how the sweep's
// provenance record is built.
func sliceOfAny(m *lab.OrderedMap, key string) []any {
	v, _ := m.Get(key)
	out, _ := v.([]any)
	return out
}
