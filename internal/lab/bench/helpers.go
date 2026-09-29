package bench

import (
	"github.com/no22/RWKV-Agent/internal/lab"
)

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

// sliceOfAny reads a key off an OrderedMap, which is how the sweep's
// provenance record is built.
func sliceOfAny(m *lab.OrderedMap, key string) []any {
	v, _ := m.Get(key)
	out, _ := v.([]any)
	return out
}
