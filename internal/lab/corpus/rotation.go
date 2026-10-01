package corpus

import (
	"crypto/sha256"
	"fmt"
	"regexp"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

// rotateCatalogs applies the v1.3 §4.2 tool-directory rotation at render time:
// with share 0.4, ~40% of the rendered rows face a work-v1 catalog missing 2-4
// tools their own trajectory never calls, so the model reads the turn's
// directory instead of reciting a memorized one. The decision is a pure
// function of the row's case ID, so re-rendering the same script reproduces
// byte-identical rows. Cases with fewer than two unused tools are left intact
// (nothing meaningful to drop); a tool the trajectory calls is never dropped.
//
// The field travels on the case (eval.Case.OfferedTools), the harness rejects
// calls to tools outside it, and the wire_hash is unaffected: it covers the
// catalog rendering mode, not the tool list.
func rotateCatalogs(cases, entries []*lab.OrderedMap, share float64) (int, error) {
	if share <= 0 || share > 1 {
		return 0, fmt.Errorf("--rotate-catalog must be in (0, 1], got %v", share)
	}
	catalog := eval.WorkToolCatalogNames()
	used := map[string]map[string]struct{}{}
	for _, entry := range entries {
		used[stringField(entry, "case_id")] = toolsUsedByEntry(entry)
	}
	rotated := 0
	for _, caseObj := range cases {
		id := stringField(caseObj, "id")
		if _, taken := caseObj.Get("offered_tools"); taken {
			continue // authored subset (§2.12) wins over the render-layer rotation
		}
		spent := used[id]
		pool := make([]string, 0, len(catalog))
		for _, name := range catalog {
			if _, wasUsed := spent[name]; !wasUsed {
				pool = append(pool, name)
			}
		}
		if len(pool) < 2 {
			continue
		}
		digest := sha256.Sum256([]byte(id))
		// One draw byte for the share decision, one for the count, one per
		// drop: stable, uniform enough, and independent per row.
		if float64(digest[0])/255.0 >= share {
			continue
		}
		nDrop := 2 + int(digest[1])%3
		if nDrop > len(pool) {
			nDrop = len(pool)
		}
		dropped := map[string]struct{}{}
		for i := 0; i < nDrop; i++ {
			pick := pool[int(digest[2+i])%len(pool)]
			dropped[pick] = struct{}{}
			kept := pool[:0]
			for _, name := range pool {
				if name != pick {
					kept = append(kept, name)
				}
			}
			pool = kept
		}
		offered := make([]any, 0, len(catalog)-len(dropped))
		for _, name := range catalog {
			if _, out := dropped[name]; !out {
				offered = append(offered, name)
			}
		}
		caseObj.Set("offered_tools", offered)
		rotated++
	}
	return rotated, nil
}

// toolCallNameRe matches the wire shape the harness itself produces:
// <tool_call>{"name":"…" — the same prefix v13_closeout.py keys on.
var toolCallNameRe = regexp.MustCompile(`<tool_call>\{"name":"([a-z_]+)"`)

// toolsUsedByEntry lists the tool names a script entry's outputs call, in the
// <tool_call>{"name":"…"} wire shape the harness itself produced.
func toolsUsedByEntry(entry *lab.OrderedMap) map[string]struct{} {
	used := map[string]struct{}{}
	outputs, _ := mapValue(entry, "outputs").([]any)
	for _, outputAny := range outputs {
		output, _ := outputAny.(*lab.OrderedMap)
		if output == nil {
			continue
		}
		rawText, _ := output.Get("text")
		text, _ := rawText.(string)
		for _, name := range toolCallNameRe.FindAllStringSubmatch(text, -1) {
			used[name[1]] = struct{}{}
		}
	}
	return used
}

