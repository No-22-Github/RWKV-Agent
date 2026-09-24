package runs

import (
	"fmt"
	"path/filepath"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Compare two workbank runs or configs case by case.
//
// For each side a per-case pass value is built: 1.0/0.0 for run directories,
// the mean over k replicas for config names. Cases are aligned by case_id and
// the report carries the flip list plus a bootstrap 95% CI of the pass-rate
// difference (A - B), resampling whole families because same-family variants
// are highly correlated.

const (
	nBoot         = 2000
	bootSeed      = 0
	passThreshold = 0.5
)

type compareCase struct {
	value    float64
	count    int
	family   string
	level    string
	traceRef string
}

// CompareArgs are the `run compare` flags.
type CompareArgs struct {
	A string
	B string
}

// RunCompare is the `run compare` command.
func RunCompare(args CompareArgs) int {
	aCases, err := loadSide(args.A)
	if err != nil {
		fmt.Fprintf(stderr, "error: %s\n", err)
		return 1
	}
	bCases, err := loadSide(args.B)
	if err != nil {
		fmt.Fprintf(stderr, "error: %s\n", err)
		return 1
	}

	var common, onlyA, onlyB []string
	for cid := range aCases {
		if _, ok := bCases[cid]; ok {
			common = append(common, cid)
		} else {
			onlyA = append(onlyA, cid)
		}
	}
	for cid := range bCases {
		if _, ok := aCases[cid]; !ok {
			onlyB = append(onlyB, cid)
		}
	}
	sort.Strings(common)
	sort.Strings(onlyA)
	sort.Strings(onlyB)

	var flipsAPassBFail, flipsAFailBPass []string
	for _, cid := range common {
		a, b := aCases[cid].value, bCases[cid].value
		if a >= passThreshold && b < passThreshold {
			flipsAPassBFail = append(flipsAPassBFail, cid)
		}
		if a < passThreshold && b >= passThreshold {
			flipsAFailBPass = append(flipsAFailBPass, cid)
		}
	}

	aVals := make([]float64, 0, len(common))
	bVals := make([]float64, 0, len(common))
	for _, cid := range common {
		aVals = append(aVals, aCases[cid].value)
		bVals = append(bVals, bCases[cid].value)
	}

	// Families are grouped in the order the sorted common list introduces them,
	// because the bootstrap indexes into this list.
	familyIndex := map[string]int{}
	var families [][]int
	for i, cid := range common {
		fam := aCases[cid].family
		if fam == "" {
			fam = bCases[cid].family
		}
		if fam == "" {
			fam = "__solo__:" + cid
		}
		idx, ok := familyIndex[fam]
		if !ok {
			families = append(families, nil)
			idx = len(families) - 1
			familyIndex[fam] = idx
		}
		families[idx] = append(families[idx], i)
	}

	lo, hi, point, hasCI := bootstrapCI(families, aVals, bVals)

	flipEntries := func(cids []string) []any {
		out := make([]any, 0, len(cids))
		for _, cid := range cids {
			entry := lab.NewOrderedMap()
			entry.Set("case", cid)
			entry.Set("a_trace", aCases[cid].traceRef)
			entry.Set("b_trace", bCases[cid].traceRef)
			out = append(out, entry)
		}
		return out
	}

	passRate := lab.NewOrderedMap()
	if len(aVals) > 0 {
		passRate.Set("a", lab.PyFloat(lab.RoundHalfEven(sum(aVals)/float64(len(aVals)), 4)))
	} else {
		passRate.Set("a", nil)
	}
	if len(bVals) > 0 {
		passRate.Set("b", lab.PyFloat(lab.RoundHalfEven(sum(bVals)/float64(len(bVals)), 4)))
	} else {
		passRate.Set("b", nil)
	}
	if len(aVals) > 0 && len(bVals) > 0 {
		passRate.Set("diff_a_minus_b", lab.PyFloat(lab.RoundHalfEven(point, 4)))
	} else {
		passRate.Set("diff_a_minus_b", nil)
	}

	ci := []any{nil, nil}
	if hasCI {
		ci = []any{lab.PyFloat(lab.RoundHalfEven(lo, 4)), lab.PyFloat(lab.RoundHalfEven(hi, 4))}
	}
	bootstrap := lab.NewOrderedMap()
	bootstrap.Set("unit", "family")
	bootstrap.Set("replicates", nBoot)
	bootstrap.Set("seed", bootSeed)
	bootstrap.Set("families", len(families))
	bootstrap.Set("ci95_a_minus_b", ci)

	flips := lab.NewOrderedMap()
	flips.Set("a_pass_b_fail", flipEntries(flipsAPassBFail))
	flips.Set("a_fail_b_pass", flipEntries(flipsAFailBPass))

	report := lab.NewOrderedMap()
	report.Set("a", args.A)
	report.Set("b", args.B)
	report.Set("common_cases", len(common))
	report.Set("pass_rate", passRate)
	report.Set("bootstrap", bootstrap)
	report.Set("flips", flips)
	report.Set("only_in_a", toAnySlice(onlyA))
	report.Set("only_in_b", toAnySlice(onlyB))

	data, err := lab.EncodeOrderedJSON(report, lab.EncodeOptions{Indent: 2})
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	fmt.Println(string(data))

	fmt.Println()
	fmt.Printf("== %s vs %s ==\n", args.A, args.B)
	fmt.Printf("common cases: %d (only in A: %d, only in B: %d)\n", len(common), len(onlyA), len(onlyB))
	if len(aVals) > 0 && len(bVals) > 0 {
		fmt.Printf("pass rate: A %.1f%%  B %.1f%%  diff (A-B) %+.1fpp\n",
			100*sum(aVals)/float64(len(aVals)), 100*sum(bVals)/float64(len(bVals)), 100*point)
		fmt.Printf("bootstrap 95%% CI of diff (family resample, n=%d): [%+.1fpp, %+.1fpp]\n",
			nBoot, 100*lo, 100*hi)
	}
	fmt.Printf("flips: A pass / B fail: %s\n", listOrNone(flipsAPassBFail))
	fmt.Printf("flips: A fail / B pass: %s\n", listOrNone(flipsAFailBPass))
	return 0
}

// bootstrapCI is a percentile CI of mean(a)-mean(b) resampling whole family
// groups. The stream is Python's random.Random(0), because these intervals are
// written into reports (P7).
func bootstrapCI(families [][]int, aVals, bVals []float64) (lo, hi, point float64, ok bool) {
	rng := lab.NewPyRandom(bootSeed)
	var diffs []float64
	nFam := len(families)
	for i := 0; i < nBoot; i++ {
		aSum, bSum, n := 0.0, 0.0, 0
		for j := 0; j < nFam; j++ {
			fam := families[rng.RandRange(nFam)]
			for _, idx := range fam {
				aSum += aVals[idx]
				bSum += bVals[idx]
				n++
			}
		}
		if n > 0 {
			diffs = append(diffs, (aSum-bSum)/float64(n))
		}
	}
	if len(diffs) == 0 {
		return 0, 0, 0, false
	}
	sort.Float64s(diffs)
	lo = diffs[int(0.025*float64(len(diffs)-1))]
	hi = diffs[int(lab.RoundHalfEven(0.975*float64(len(diffs)-1), 0))]
	point = sum(aVals)/float64(len(aVals)) - sum(bVals)/float64(len(bVals))
	return lo, hi, point, true
}

func sum(values []float64) float64 {
	total := 0.0
	for _, v := range values {
		total += v
	}
	return total
}

func loadSide(arg string) (map[string]compareCase, error) {
	if info, err := statPath(arg); err == nil && info {
		return loadRunDir(arg)
	}
	return loadConfig(arg)
}

func loadRunDir(runDir string) (map[string]compareCase, error) {
	summary, err := LoadJSONFile(filepath.Join(runDir, "summary.json"), false)
	if err != nil || summary == nil {
		return nil, fmt.Errorf("%s is not a run directory", runDir)
	}
	manifest, err := LoadJSONFile(filepath.Join(runDir, "run.json"), false)
	if err != nil || manifest == nil {
		return nil, fmt.Errorf("%s is not a run directory", runDir)
	}
	tagsByID := map[string]map[string]any{}
	for _, c := range mapSlice(manifest["cases"]) {
		if id, ok := c["id"].(string); ok {
			tagsByID[id] = mapOf(c, "tags")
		}
	}
	cases := map[string]compareCase{}
	for _, c := range mapSlice(summary["cases"]) {
		cid, ok := c["id"].(string)
		if !ok {
			continue
		}
		tags := mapOf(c, "tags")
		if len(tags) == 0 {
			tags = tagsByID[cid]
		}
		if tags == nil {
			tags = map[string]any{}
		}
		value := 0.0
		if passed, _ := c["passed"].(bool); passed {
			value = 1.0
		}
		family, _ := tags["family"].(string)
		cases[cid] = compareCase{
			value:    value,
			count:    1,
			family:   family,
			level:    stringOf(tags, "level"),
			traceRef: fmt.Sprintf("%s#%s", runDir, cid),
		}
	}
	return cases, nil
}

func loadConfig(configName string) (map[string]compareCase, error) {
	cases := map[string]compareCase{}
	var order []string
	for _, r := range ReadJSONL(DefaultLedgerCases()) {
		if stringOf(r, "config_name") != configName {
			continue
		}
		cid, ok := r["case_id"].(string)
		if !ok {
			continue
		}
		entry, seen := cases[cid]
		if !seen {
			entry = compareCase{traceRef: stringOf(r, "trace_ref")}
			order = append(order, cid)
		}
		if passed, _ := r["passed"].(bool); passed {
			entry.value += 1.0
		}
		entry.count++
		if entry.family == "" {
			entry.family = stringOf(r, "family")
		}
		if entry.level == "" {
			entry.level = stringOf(r, "level")
		}
		cases[cid] = entry
	}
	if len(order) == 0 {
		return nil, fmt.Errorf("no ledger rows for config_name %s in %s", pyQuote(configName), DefaultLedgerCases())
	}
	for _, cid := range order {
		entry := cases[cid]
		entry.value = entry.value / float64(entry.count)
		cases[cid] = entry
	}
	return cases, nil
}

func listOrNone(items []string) string {
	if len(items) == 0 {
		return "none"
	}
	parts := make([]string, 0, len(items))
	for _, item := range items {
		parts = append(parts, pyQuote(item))
	}
	return "[" + strings.Join(parts, ", ") + "]"
}
