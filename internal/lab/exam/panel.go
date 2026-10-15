package exam

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// The capability panel scores a run along the exam's own axes, so a total
// that moved can be traced to the task kind, difficulty or language behind it.

type panelRun struct {
	name   string
	passed map[string]bool
}

func loadPanelRun(dir string) (panelRun, error) {
	data, err := os.ReadFile(filepath.Join(dir, "summary.json"))
	if err != nil {
		return panelRun{}, err
	}
	var summary struct {
		Cases []struct {
			ID     string `json:"id"`
			Passed bool   `json:"passed"`
		} `json:"cases"`
	}
	if err := json.Unmarshal(data, &summary); err != nil {
		return panelRun{}, fmt.Errorf("%s: %w", dir, err)
	}
	run := panelRun{name: filepath.Base(dir), passed: map[string]bool{}}
	for _, c := range summary.Cases {
		run.passed[c.ID] = c.Passed
	}
	return run, nil
}

type panelRow struct {
	label string
	keep  func(eval.ExamCase) bool
}

func panelRows() []panelRow {
	rows := []panelRow{{"总分", func(eval.ExamCase) bool { return true }}}
	for _, task := range TaskOrder {
		task := task
		rows = append(rows, panelRow{"任务 · " + TaskLabel[task], func(c eval.ExamCase) bool { return c.Task == task }})
	}
	for _, diff := range DifficultyOrder {
		diff := diff
		rows = append(rows, panelRow{"难点 · " + DifficultyLabel[diff], func(c eval.ExamCase) bool {
			return containsString(c.Difficulties, diff)
		}})
	}
	for _, language := range []string{"zh", "en"} {
		language := language
		rows = append(rows, panelRow{"语言 · " + languageLabel(language), func(c eval.ExamCase) bool { return c.Language == language }})
	}
	for _, source := range Sources {
		source := source
		rows = append(rows, panelRow{"来源 · " + source.Label, func(c eval.ExamCase) bool { return c.Suite == source.Name }})
	}
	return rows
}

func runPanel(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab exam panel", flag.ContinueOnError)
	manifestPath := flags.String("manifest", "", "exam manifest the runs used (default: bench/exam/full.json, or quick.json when every run has fewer cases)")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	if flags.NArg() == 0 {
		fmt.Fprintln(os.Stderr, "usage: rwkv-lab exam panel [--manifest m.json] <run dir>...")
		return 2
	}
	var runs []panelRun
	for _, dir := range flags.Args() {
		run, err := loadPanelRun(dir)
		if err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab exam panel:", err)
			return 1
		}
		runs = append(runs, run)
	}
	if *manifestPath == "" {
		*manifestPath = filepath.Join(DefaultPaths().ExamDir, "full.json")
		quick := true
		for _, run := range runs {
			if len(run.passed) > 100 {
				quick = false
			}
		}
		if quick {
			*manifestPath = filepath.Join(DefaultPaths().ExamDir, "quick.json")
		}
	}
	manifest, err := eval.ReadExamManifest(*manifestPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam panel:", err)
		return 1
	}
	header := "| 维度 | 题数 |"
	rule := "|---|---|"
	for _, run := range runs {
		header += " " + run.name + " |"
		rule += "---|"
	}
	fmt.Println(header)
	fmt.Println(rule)
	for _, row := range panelRows() {
		var members []eval.ExamCase
		for _, c := range manifest.Cases {
			if row.keep(c) {
				members = append(members, c)
			}
		}
		if len(members) == 0 {
			continue
		}
		line := fmt.Sprintf("| %s | %d |", row.label, len(members))
		for _, run := range runs {
			passed, seen := 0, 0
			for _, c := range members {
				if ok, present := run.passed[c.ID]; present {
					seen++
					if ok {
						passed++
					}
				}
			}
			if seen == 0 {
				line += " — |"
				continue
			}
			cell := fmt.Sprintf(" %d/%d（%.0f%%）", passed, seen, 100*float64(passed)/float64(seen))
			if seen < len(members) {
				cell += " 缺题"
			}
			line += cell + " |"
		}
		fmt.Println(strings.TrimRight(line, " "))
	}
	return 0
}
