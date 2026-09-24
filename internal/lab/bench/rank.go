package bench

import (
	"encoding/json"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab/runs"
)

// Rank sampling arms from sweep runs using the pre-registered rules
// (docs/evaluations/g1k-sampling-sweep-20260923/PLAN.md):
//
//   - only runs whose experiment.json has gate_passed=true count; strict score
//     is correct / all cases
//   - primary: workbank strict mean over replicas
//   - stage 1 (k=1): rank by workbank + bfcl-product strict (combined)
//   - floor: if every arm's workbank best <= --floor, workbank has no
//     resolution; rank by combined
//   - stage 2 (k>=2): rank by workbank mean; if #1 - #2 <= max(range #1,
//     range #2) they are indistinguishable -> break by bfcl-product mean ->
//     then by lower temperature
//
// Paired flips vs --baseline use replica k0 on workbank, with a two-sided sign
// test.

var runNameRe = regexp.MustCompile(`^(.+?)-(workbank|bfclp|boundary|assistant|smoke|porig30|pfb30)-(.+)-k(\d+)$`)

type rankRep struct {
	path    string
	meta    map[string]any
	scores  map[string]bool
	correct int
	total   int
	invalid int
}

type rankStats struct {
	values         []int
	mean           float64
	rng            int
	total          int
	k              int
	invalid        int
	keptWithErrors int
}

// RankArgs are the `bench rank` flags.
type RankArgs struct {
	Out      string
	Prefix   string
	Baseline string
	Floor    int
	Save     string
}

// RunRank is the `bench rank` command.
func RunRank(args RankArgs) int {
	loaded := loadRankRuns(args.Out, args.Prefix)
	arms := map[string]bool{}
	for key := range loaded {
		arms[key.arm] = true
	}
	armNames := make([]string, 0, len(arms))
	for arm := range arms {
		armNames = append(armNames, arm)
	}
	sort.Strings(armNames)
	if len(armNames) == 0 {
		fmt.Fprintln(os.Stderr, "no gated runs found")
		return 1
	}

	type tableEntry struct {
		wb *rankStats
		bp *rankStats
	}
	table := map[string]tableEntry{}
	for _, arm := range armNames {
		table[arm] = tableEntry{
			wb: statsFor(loaded[rankKey{"workbank", arm}]),
			bp: statsFor(loaded[rankKey{"bfclp", arm}]),
		}
	}

	lines := []string{fmt.Sprintf("# 采样扫描排名（%s）", args.Out), ""}

	var wbBest []int
	for _, arm := range armNames {
		if table[arm].wb != nil {
			wbBest = append(wbBest, maxInt(table[arm].wb.values))
		}
	}
	floor := len(wbBest) > 0 && maxInt(wbBest) <= args.Floor
	var staged []string
	for _, arm := range armNames {
		if table[arm].wb != nil && table[arm].wb.k >= 2 {
			staged = append(staged, arm)
		}
	}
	stage := 1
	if len(staged) >= 2 {
		stage = 2
	}

	combined := func(arm string) float64 {
		total := 0.0
		if table[arm].wb != nil {
			total += table[arm].wb.mean
		}
		if table[arm].bp != nil {
			total += table[arm].bp.mean
		}
		return total
	}

	var order []string
	rule := ""
	if stage == 1 || floor {
		order = append([]string(nil), armNames...)
		sort.SliceStable(order, func(i, j int) bool {
			ci, cj := combined(order[i]), combined(order[j])
			if ci != cj {
				return ci > cj
			}
			return temperatureOf(loaded, order[i]) < temperatureOf(loaded, order[j])
		})
		rule = "综合分（workbank + bfcl-product）"
		if floor {
			rule += "；**地板规则触发**：workbank 无区分度"
		}
	} else {
		order = append([]string(nil), staged...)
		sort.SliceStable(order, func(i, j int) bool {
			mi, mj := table[order[i]].wb.mean, table[order[j]].wb.mean
			if mi != mj {
				return mi > mj
			}
			return temperatureOf(loaded, order[i]) < temperatureOf(loaded, order[j])
		})
		rule = "workbank 均值（k≥2 的档）"
		if len(order) >= 2 {
			first, second := table[order[0]].wb, table[order[1]].wb
			if first.mean-second.mean <= float64(maxInt([]int{first.rng, second.rng})) {
				bp := func(a string) float64 {
					if table[a].bp != nil {
						return table[a].bp.mean
					}
					return 0
				}
				head := append([]string(nil), order[:2]...)
				sort.SliceStable(head, func(i, j int) bool {
					if bp(head[i]) != bp(head[j]) {
						return bp(head[i]) > bp(head[j])
					}
					return temperatureOf(loaded, head[i]) < temperatureOf(loaded, head[j])
				})
				order = append(head, order[2:]...)
				rule += fmt.Sprintf("；前两名差 %.1f ≤ 极差，视为无法区分 → 按 bfcl-product 均值，再按低温度",
					first.mean-second.mean)
			}
		}
	}

	lines = append(lines,
		fmt.Sprintf("阶段 %d，排序依据：%s", stage, rule), "",
		"| # | 档 | workbank strict | bfcl-product strict | 综合 |",
		"|---|---|---|---|---|")
	for i, arm := range order {
		lines = append(lines, fmt.Sprintf("| %d | `%s` | %s | %s | %.1f |",
			i+1, arm, fmtRank(table[arm].wb), fmtRank(table[arm].bp), combined(arm)))
	}
	for _, arm := range armNames {
		if containsString(order, arm) {
			continue
		}
		lines = append(lines, fmt.Sprintf("| – | `%s` | %s | %s | %.1f |",
			arm, fmtRank(table[arm].wb), fmtRank(table[arm].bp), combined(arm)))
	}

	if base := repAt(loaded, rankKey{"workbank", args.Baseline}, 0); base != nil {
		lines = append(lines, "", fmt.Sprintf("## workbank 逐题配对（k0，对照 `%s`）", args.Baseline), "",
			"| 档 | +翻正 | −翻负 | 符号检验 p |", "|---|---|---|---|")
		for _, arm := range order {
			other := repAt(loaded, rankKey{"workbank", arm}, 0)
			if arm == args.Baseline || other == nil {
				continue
			}
			plus, minus := 0, 0
			for cid, basePassed := range base.scores {
				otherPassed, ok := other.scores[cid]
				if !ok {
					continue
				}
				if otherPassed && !basePassed {
					plus++
				}
				if basePassed && !otherPassed {
					minus++
				}
			}
			lines = append(lines, fmt.Sprintf("| `%s` | +%d | −%d | %.3f |",
				arm, plus, minus, signTest(plus, minus)))
		}
	}

	var kept []string
	for _, arm := range armNames {
		for _, s := range []*rankStats{table[arm].wb, table[arm].bp} {
			if s != nil && s.keptWithErrors > 0 {
				kept = append(kept, arm)
				break
			}
		}
	}
	if len(kept) > 0 {
		quoted := make([]string, 0, len(kept))
		for _, arm := range kept {
			quoted = append(quoted, "`"+arm+"`")
		}
		lines = append(lines, "", "⚠ 这些档有 run 在最后一次尝试仍带基础设施错误，已按规程把作废计为失败保留："+
			strings.Join(quoted, ", "))
	}

	// Python prints the joined text with print(), which adds a second newline.
	text := strings.Join(lines, "\n") + "\n"
	fmt.Println(text)
	if args.Save != "" {
		if err := os.WriteFile(args.Save, []byte(text), 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			return 1
		}
	}
	return 0
}

type rankKey struct {
	suite string
	arm   string
}

// loadRankRuns indexes gated runs by (suite, arm) -> [k]record. A run counts
// only when its experiment.json says gate_passed.
func loadRankRuns(out, prefix string) map[rankKey][]*rankRep {
	entries, err := os.ReadDir(out)
	if err != nil {
		return nil
	}
	names := make([]string, 0, len(entries))
	for _, entry := range entries {
		names = append(names, entry.Name())
	}
	sort.Strings(names)

	loaded := map[rankKey][]*rankRep{}
	for _, name := range names {
		path := filepath.Join(out, name)
		match := runNameRe.FindStringSubmatch(name)
		if match == nil || match[1] != prefix {
			continue
		}
		info, err := os.Stat(path)
		if err != nil || !info.IsDir() {
			continue
		}
		metaPath := filepath.Join(path, "experiment.json")
		if !exists(metaPath) {
			continue
		}
		meta, err := runs.LoadJSONFile(metaPath, true)
		if err != nil {
			continue
		}
		if passed, _ := meta["gate_passed"].(bool); !passed {
			continue
		}
		summary, err := runs.LoadJSONFile(filepath.Join(path, "summary.json"), true)
		if err != nil {
			continue
		}
		k, err := strconv.Atoi(match[4])
		if err != nil {
			continue
		}
		scores := map[string]bool{}
		correct, invalid := 0, 0
		for _, c := range mapSlice(summary["cases"]) {
			passed, _ := c["passed"].(bool)
			isInvalid, _ := c["invalid"].(bool)
			ok := passed && !isInvalid
			scores[stringOf(c, "id")] = ok
			if ok {
				correct++
			}
			if isInvalid {
				invalid++
			}
		}
		key := rankKey{match[2], match[3]}
		reps := loaded[key]
		for len(reps) <= k {
			reps = append(reps, nil)
		}
		reps[k] = &rankRep{
			path: path, meta: meta, scores: scores,
			correct: correct, total: len(scores), invalid: invalid,
		}
		loaded[key] = reps
	}
	return loaded
}

func statsFor(reps []*rankRep) *rankStats {
	var present []*rankRep
	for _, r := range reps {
		if r != nil {
			present = append(present, r)
		}
	}
	if len(present) == 0 {
		return nil
	}
	out := &rankStats{k: len(present)}
	for _, r := range present {
		out.values = append(out.values, r.correct)
		out.total = r.total
		out.invalid += r.invalid
		if kept, _ := r.meta["accepted_with_infra_errors"].(bool); kept {
			out.keptWithErrors++
		}
	}
	total := 0
	for _, v := range out.values {
		total += v
	}
	out.mean = float64(total) / float64(len(out.values))
	out.rng = maxInt(out.values) - minInt(out.values)
	return out
}

func fmtRank(s *rankStats) string {
	if s == nil {
		return "—"
	}
	parts := make([]string, 0, len(s.values))
	for _, v := range s.values {
		parts = append(parts, strconv.Itoa(v))
	}
	vals := strings.Join(parts, "/")
	text := ""
	if s.k > 1 {
		text = fmt.Sprintf("%.1f/%d", s.mean, s.total)
	} else {
		text = fmt.Sprintf("%s/%d", vals, s.total)
	}
	if s.k > 1 {
		text += fmt.Sprintf(" (k=%d: %s, range %d)", s.k, vals, s.rng)
	}
	if s.invalid > 0 {
		text += fmt.Sprintf(" ⚠ invalid %d", s.invalid)
	}
	return text
}

// repAt reads one replica. The slice is indexed by k and may be sparse, so a
// missing k is nil rather than a panic.
func repAt(loaded map[rankKey][]*rankRep, key rankKey, k int) *rankRep {
	reps := loaded[key]
	if k >= len(reps) {
		return nil
	}
	return reps[k]
}

// temperatureOf is the arm's sampling temperature. Keys are walked in sorted
// order because Python's dict iteration follows the sorted directory listing
// and this must not depend on Go's map order.
func temperatureOf(loaded map[rankKey][]*rankRep, arm string) float64 {
	keys := make([]rankKey, 0, len(loaded))
	for key := range loaded {
		if key.arm == arm {
			keys = append(keys, key)
		}
	}
	sort.Slice(keys, func(i, j int) bool {
		if keys[i].suite != keys[j].suite {
			return keys[i].suite < keys[j].suite
		}
		return keys[i].arm < keys[j].arm
	})
	for _, key := range keys {
		for _, r := range loaded[key] {
			if r == nil {
				continue
			}
			sampling, _ := r.meta["sampling"].(map[string]any)
			if sampling == nil {
				continue
			}
			if t, ok := numberValue(sampling["temperature"]); ok {
				return t
			}
		}
	}
	return 99
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

// signTest is a two-sided sign test over the paired flips.
func signTest(plus, minus int) float64 {
	n := plus + minus
	if n == 0 {
		return 1.0
	}
	smaller := plus
	if minus < smaller {
		smaller = minus
	}
	tail := 0.0
	for i := 0; i <= smaller; i++ {
		tail += float64(comb(n, i))
	}
	tail /= math.Pow(2, float64(n))
	return math.Min(1.0, 2*tail)
}

func comb(n, k int) int64 {
	if k < 0 || k > n {
		return 0
	}
	result := int64(1)
	for i := 1; i <= k; i++ {
		result = result * int64(n-k+i) / int64(i)
	}
	return result
}

func maxInt(values []int) int {
	if len(values) == 0 {
		return 0
	}
	best := values[0]
	for _, v := range values[1:] {
		if v > best {
			best = v
		}
	}
	return best
}

func minInt(values []int) int {
	if len(values) == 0 {
		return 0
	}
	best := values[0]
	for _, v := range values[1:] {
		if v < best {
			best = v
		}
	}
	return best
}

func containsString(list []string, want string) bool {
	for _, item := range list {
		if item == want {
			return true
		}
	}
	return false
}
