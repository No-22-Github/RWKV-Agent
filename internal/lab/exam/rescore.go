package exam

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// rescore re-judges finished runs against the current scorer and case files,
// without rerunning the model: an exam revision that only changes judging is
// priced on the runs already on disk. Case-level end-state checks cannot be
// recomputed from the record and are carried over (eval.Rescore).

type rescoreRun struct {
	dir     string
	harness string
	cases   []eval.CaseResult
}

func loadRescoreRun(dir string) (rescoreRun, error) {
	run := rescoreRun{dir: dir}
	data, err := os.ReadFile(filepath.Join(dir, "summary.json"))
	if err != nil {
		return run, err
	}
	var summary struct {
		Cases []eval.CaseResult `json:"cases"`
	}
	if err := json.Unmarshal(data, &summary); err != nil {
		return run, fmt.Errorf("%s: %w", dir, err)
	}
	run.cases = summary.Cases
	if data, err := os.ReadFile(filepath.Join(dir, "run.json")); err == nil {
		var record struct {
			Harness struct {
				ProductHarness string `json:"product_harness"`
			} `json:"harness"`
		}
		if json.Unmarshal(data, &record) == nil {
			run.harness = record.Harness.ProductHarness
		}
	}
	return run, nil
}

func runRescore(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab exam rescore", flag.ContinueOnError)
	manifestPath := flags.String("manifest", filepath.Join(DefaultPaths().ExamDir, "full.json"), "exam manifest whose case files hold the expectations to judge by")
	flipsPath := flags.String("flips", "", "write every case that changed verdict to this TSV")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	if flags.NArg() == 0 {
		fmt.Fprintln(os.Stderr, "usage: rwkv-lab exam rescore [--manifest m.json] [--flips out.tsv] <run dir>...")
		return 2
	}
	_, cases, err := eval.LoadCasesManifest(*manifestPath, "")
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam rescore:", err)
		return 1
	}
	byID := make(map[string]eval.Case, len(cases))
	for _, testCase := range cases {
		byID[testCase.ID] = testCase
	}
	flips := []string{"run\tid\tchange\treason"}
	fmt.Println("| run | 计分题数 | 旧分 | 新分 | 改判对 | 改判错 |")
	fmt.Println("|---|---|---|---|---|---|")
	for _, dir := range flags.Args() {
		run, err := loadRescoreRun(dir)
		if err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab exam rescore:", err)
			return 1
		}
		scored, old, now, gained, lost := 0, 0, 0, 0, 0
		for _, caseResult := range run.cases {
			if caseResult.Invalid {
				continue
			}
			scored++
			next := caseResult
			if testCase, ok := byID[caseResult.ID]; ok {
				next = eval.Rescore(testCase, caseResult, eval.IsProductHarness(run.harness))
			}
			if caseResult.Passed {
				old++
			}
			if next.Passed {
				now++
			}
			switch {
			case next.Passed && !caseResult.Passed:
				gained++
				flips = append(flips, strings.Join([]string{dir, caseResult.ID, "fail→pass", firstFailures(caseResult)}, "\t"))
			case !next.Passed && caseResult.Passed:
				lost++
				flips = append(flips, strings.Join([]string{dir, caseResult.ID, "pass→fail", firstFailures(next)}, "\t"))
			}
		}
		fmt.Printf("| %s | %d | %d | %d | +%d | −%d |\n", dir, scored, old, now, gained, lost)
	}
	if *flipsPath != "" {
		sort.Strings(flips[1:])
		if err := os.WriteFile(*flipsPath, []byte(strings.Join(flips, "\n")+"\n"), 0o644); err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab exam rescore:", err)
			return 1
		}
	}
	return 0
}

// firstFailures is a one-line account of why a case failed.
func firstFailures(result eval.CaseResult) string {
	var reasons []string
	reasons = append(reasons, result.Failures...)
	for _, turn := range result.Turns {
		for _, failure := range turn.Failures {
			reasons = append(reasons, fmt.Sprintf("t%d %s", turn.Number, failure))
		}
	}
	line := strings.Join(reasons, " | ")
	line = strings.NewReplacer("\t", " ", "\n", " ").Replace(line)
	if runes := []rune(line); len(runes) > 300 {
		line = string(runes[:300]) + "…"
	}
	return line
}
