package bank

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// tolerance is the +/-1 case slack per level per scenario (HANDOFF.md §6).
const tolerance = 1

// runCoverage ports coverage.py. It is a planning tool, not a gate: exit code
// is always 0, and lint.py is what fails a bank.
func runCoverage(args []string) int {
	fs := newFlagSet("bank coverage",
		"Report scenario x level coverage of the workbank case tree against the quotas.")
	cases := fs.String("cases", DefaultCases(), "cases root directory")
	vocabPath := fs.String("vocab", DefaultVocab(), "tag vocabulary file with quotas")
	gaps := fs.Bool("gaps", false, "print only the gaps")
	summary := fs.Bool("summary", false, "print the full fill table")
	if err := fs.Parse(args); err != nil {
		return 2
	}

	vocab, err := loadVocab(*vocabPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		return 2
	}
	cells, err := countScenarioLevels(*cases)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		return 2
	}

	showAll := *summary || !*gaps
	showGaps := *gaps || !*summary

	var gapLines []string
	total := 0
	for _, entry := range vocab.scenarios {
		name, quota := entry.name, entry.quota
		want := expectedCounts(quota, vocab.mix)
		have := map[string]int{}
		filled := 0
		for _, level := range vocab.levels {
			have[level] = cells[name+"\x00"+level]
			filled += have[level]
		}
		total += filled
		if showAll {
			row := ""
			for i, level := range vocab.levels {
				if i > 0 {
					row += "  "
				}
				row += fmt.Sprintf("%s %2d/%-2d", level, have[level], want[level])
			}
			fmt.Printf("%-10s (%3d slots, filled %3d): %s\n", name, quota, filled, row)
		}
		for _, level := range vocab.levels {
			delta := have[level] - want[level]
			if delta < -tolerance {
				gapLines = append(gapLines,
					fmt.Sprintf("  %-10s %s: need %d, have %d (short %d)", name, level, want[level], have[level], -delta))
			} else if delta > tolerance {
				gapLines = append(gapLines,
					fmt.Sprintf("  %-10s %s: quota %d, have %d (over by %d)", name, level, want[level], have[level], delta))
			}
		}
	}

	if showGaps {
		if len(gapLines) > 0 {
			fmt.Printf("gaps (%d):\n", len(gapLines))
			for _, line := range gapLines {
				fmt.Println(line)
			}
		} else {
			fmt.Println("no gaps: every scenario is within +/-1 of its level mix")
		}
	}
	fmt.Fprintf(os.Stderr, "total cases filled: %d\n", total)
	return 0
}

// expectedCounts is the largest-remainder split of a scenario quota across the
// levels. Python's sorted() is stable, so levels with the same remainder keep
// the order they appear in level_mix; that order is read from the file rather
// than from a Go map, which has none.
func expectedCounts(quota int, mix []levelShare) map[string]int {
	raw := make([]float64, len(mix))
	base := make(map[string]int, len(mix))
	sum := 0
	for i, entry := range mix {
		raw[i] = float64(quota) * entry.share
		base[entry.level] = int(raw[i]) // Python's int(x // 1) is floor for x >= 0
		sum += base[entry.level]
	}
	order := make([]int, len(mix))
	for i := range order {
		order[i] = i
	}
	sort.SliceStable(order, func(a, b int) bool {
		return raw[order[a]]-float64(base[mix[order[a]].level]) > raw[order[b]]-float64(base[mix[order[b]].level])
	})
	if len(order) == 0 {
		return base
	}
	short := quota - sum
	for i := 0; i < short; i++ {
		base[mix[order[i%len(order)]].level]++
	}
	return base
}

func countScenarioLevels(root string) (map[string]int, error) {
	dirs, err := findCaseFiles(root)
	if err != nil {
		return nil, err
	}
	cells := map[string]int{}
	for _, dir := range dirs {
		caseObj, err := loadCaseJSON(filepath.Join(dir, "case.json"))
		if err != nil {
			continue
		}
		tags := tagsOf(caseObj)
		scenario, scenarioOK := tags["scenario"].(string)
		level, levelOK := tags["level"].(string)
		if scenarioOK && levelOK {
			cells[scenario+"\x00"+level]++
		}
	}
	return cells, nil
}

type levelShare struct {
	level string
	share float64
}

type vocab struct {
	scenarios []scenarioEntry
	levels    []string
	mix       []levelShare
}

type scenarioEntry struct {
	name   string
	abbrev string
	quota  int
}

// loadVocab reads the pieces coverage needs. level_mix is decoded in source
// order because the largest-remainder tie-break depends on it.
func loadVocab(path string) (*vocab, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	obj, err := lab.DecodeJSONBytes(raw)
	if err != nil {
		return nil, err
	}
	m, ok := obj.(map[string]any)
	if !ok {
		return nil, fmt.Errorf("%s is not a JSON object", path)
	}
	out := &vocab{}
	for _, entry := range anySlice(m["scenarios"]) {
		em, _ := entry.(map[string]any)
		out.scenarios = append(out.scenarios, scenarioEntry{
			name:   stringField(em, "name"),
			abbrev: stringField(em, "abbrev"),
			quota:  intField(em, "quota"),
		})
	}
	for _, level := range anySlice(m["levels"]) {
		if s, ok := level.(string); ok {
			out.levels = append(out.levels, s)
		}
	}
	mixRaw, err := lab.OrderedObjectKeys(raw, "level_mix")
	if err != nil {
		return nil, err
	}
	mixObj, _ := m["level_mix"].(map[string]any)
	for _, level := range mixRaw {
		out.mix = append(out.mix, levelShare{level: level, share: floatField(mixObj, level)})
	}
	return out, nil
}

func anySlice(v any) []any {
	s, _ := v.([]any)
	return s
}

func intField(m map[string]any, key string) int {
	if n, ok := m[key].(json.Number); ok {
		if i, err := n.Int64(); err == nil {
			return int(i)
		}
		if f, err := n.Float64(); err == nil {
			return int(f)
		}
	}
	return 0
}

func floatField(m map[string]any, key string) float64 {
	if n, ok := m[key].(json.Number); ok {
		if f, err := n.Float64(); err == nil {
			return f
		}
	}
	return 0
}
