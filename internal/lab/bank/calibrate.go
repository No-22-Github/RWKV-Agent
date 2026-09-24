package bank

import (
	"fmt"
	"os"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// runCalibrate ports calibrate.py: aggregate ledger/cases.jsonl across every
// run and flag cases whose measured pass rate contradicts tags.level.
//
// Note on --ledger: the Python original parses the flag but its collect()
// reads the module-level CASES_JSONL path, so the flag never changed which
// file was read — it only appears in the "no cases in ledger" message. §1 of
// the migration doc says not to fix bugs found on the way, so this port keeps
// that behaviour and the defect is recorded in §7 instead. If the flag is
// meant to work, that is a follow-up, not part of the migration.
func runCalibrate(args []string) int {
	fs := newFlagSet("bank calibrate",
		"Flag cases whose measured pass rate contradicts their declared difficulty level.")
	ledger := fs.String("ledger", DefaultLedgerCases(), "path to cases.jsonl")
	if err := fs.Parse(args); err != nil {
		return 2
	}

	perCase, order := collectLedger(DefaultLedgerCases())
	if len(perCase) == 0 {
		fmt.Printf("no cases in ledger (%s)\n", *ledger)
		return 0
	}

	type entry struct {
		cs      string
		level   string
		flag    string
		configs string
		overall string
	}
	entries := make([]entry, 0, len(perCase))
	ids := append([]string(nil), order...)
	sort.Strings(ids)
	for _, cid := range ids {
		d := perCase[cid]
		totalP, totalN := d.total[0], d.total[1]
		overall := 0.0
		hasOverall := totalN > 0
		if hasOverall {
			overall = float64(totalP) / float64(totalN)
		}
		var rates []float64
		for _, cfg := range d.configOrder {
			g := d.configs[cfg]
			if g[1] > 0 {
				rates = append(rates, float64(g[0])/float64(g[1]))
			}
		}
		flag := classify(d.level, rates, overall, hasOverall)

		cfgs := make([]string, 0, len(d.configs))
		for cfg := range d.configs {
			cfgs = append(cfgs, cfg)
		}
		sort.Strings(cfgs)
		configCell := ""
		for i, cfg := range cfgs {
			if i > 0 {
				configCell += ", "
			}
			g := d.configs[cfg]
			configCell += fmt.Sprintf("%s %.0f%%", cfg, 100*float64(g[0])/float64(g[1]))
		}
		overallCell := "-"
		if hasOverall {
			overallCell = fmt.Sprintf("%.0f%% (%d/%d)", 100*overall, totalP, totalN)
		}
		level := d.level
		if level == "" {
			level = "unknown"
		}
		entries = append(entries, entry{cid, level, flag, configCell, overallCell})
	}

	flagged := 0
	for _, e := range entries {
		if e.flag != "-" {
			flagged++
		}
	}
	sort.SliceStable(entries, func(i, j int) bool {
		// Flagged rows first, then by case id (Python: key=(flag == "-", case)).
		gi, gj := entries[i].flag == "-", entries[j].flag == "-"
		if gi != gj {
			return !gi
		}
		return entries[i].cs < entries[j].cs
	})

	fmt.Println("# workbank calibration (declared level vs measured pass rate)")
	fmt.Println()
	fmt.Println("| case | level | per-config pass | overall | flag |")
	fmt.Println("|---|---|---|---|---|")
	for _, e := range entries {
		fmt.Printf("| %s | %s | %s | %s | %s |\n", e.cs, e.level, e.configs, e.overall, e.flag)
	}
	fmt.Println()
	fmt.Printf("flagged %d / %d cases; rules: L1/L2 all-config <20%% => harder_than_declined, "+
		"L3 all-config >80%% => easier_than_declined, L0 <50%% => l0_too_hard\n", flagged, len(entries))
	return 0
}

func classify(level string, configRates []float64, overall float64, hasOverall bool) string {
	switch level {
	case "L1", "L2":
		if len(configRates) > 0 && allLess(configRates, 0.20) {
			return "harder_than_declined"
		}
	case "L3":
		if len(configRates) > 0 && allGreater(configRates, 0.80) {
			return "easier_than_declined"
		}
	case "L0":
		if hasOverall && overall < 0.50 {
			return "l0_too_hard"
		}
	}
	return "-"
}

func allLess(xs []float64, limit float64) bool {
	for _, x := range xs {
		if !(x < limit) {
			return false
		}
	}
	return true
}

func allGreater(xs []float64, limit float64) bool {
	for _, x := range xs {
		if !(x > limit) {
			return false
		}
	}
	return true
}

type caseAgg struct {
	level       string
	configs     map[string][2]int
	configOrder []string
	total       [2]int
}

func collectLedger(path string) (map[string]*caseAgg, []string) {
	perCase := map[string]*caseAgg{}
	var order []string
	for i, line := range lab.SplitLines(readTextOrEmpty(path)) {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		rowAny, err := lab.DecodeJSONBytes([]byte(line))
		if err != nil {
			fmt.Fprintf(os.Stderr, "warning: %s:%d is not valid JSON, skipped\n", path, i+1)
			continue
		}
		row, ok := rowAny.(map[string]any)
		if !ok {
			fmt.Fprintf(os.Stderr, "warning: %s:%d is not valid JSON, skipped\n", path, i+1)
			continue
		}
		cid, ok := row["case_id"].(string)
		if !ok {
			continue
		}
		d, seen := perCase[cid]
		if !seen {
			d = &caseAgg{configs: map[string][2]int{}}
			perCase[cid] = d
			order = append(order, cid)
		}
		if d.level == "" {
			if lvl, ok := row["level"].(string); ok {
				d.level = lvl
			}
		}
		cfg, ok := row["config_name"].(string)
		if !ok || cfg == "" {
			cfg = "unknown"
		}
		g, seenCfg := d.configs[cfg]
		if !seenCfg {
			d.configOrder = append(d.configOrder, cfg)
		}
		g[1]++
		d.total[1]++
		if passed, _ := row["passed"].(bool); passed {
			g[0]++
			d.total[0]++
		}
		d.configs[cfg] = g
	}
	return perCase, order
}

func readTextOrEmpty(path string) string {
	text, err := lab.ReadText(path)
	if err != nil {
		return ""
	}
	return text
}
