package geval

import (
	"encoding/json"
	"flag"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"strings"
)

func runReport(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab geval report", flag.ContinueOnError)
	if err := flags.Parse(args); err != nil {
		return 2
	}
	if flags.NArg() == 0 {
		fmt.Fprintln(os.Stderr, "usage: rwkv-lab geval report <scored run dir>...  (first run is the baseline for flips)")
		return 2
	}
	var runs []runSummary
	for _, dir := range flags.Args() {
		var s runSummary
		data, err := os.ReadFile(filepath.Join(dir, "summary.json"))
		if err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab geval report:", err, "(run `geval score` first)")
			return 1
		}
		if err := json.Unmarshal(data, &s); err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab geval report:", err)
			return 1
		}
		runs = append(runs, s)
	}
	fmt.Print(renderTable(runs))
	if len(runs) > 1 {
		out, err := renderFlips(flags.Args())
		if err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab geval report:", err)
			return 1
		}
		fmt.Print(out)
	}
	return 0
}

func runLabel(s runSummary) string {
	label := filepath.Base(s.Dir)
	if s.Config.AdapterID != "" {
		label += " (" + s.Config.AdapterID + ")"
	}
	return label
}

// renderTable is the score table (one column per run) followed by the
// output statistics.
func renderTable(runs []runSummary) string {
	var b strings.Builder
	b.WriteString("\n### 分数\n\n| 项 | 指标 |")
	for _, r := range runs {
		b.WriteString(" " + runLabel(r) + " |")
	}
	b.WriteString("\n|---|---|" + strings.Repeat("---:|", len(runs)) + "\n")
	metricOrder := map[string][]string{
		TaskIFEvalEN:  {"prompt_strict", "inst_strict", "prompt_loose", "inst_loose"},
		TaskIFEvalZH:  {"prompt_strict", "inst_strict", "prompt_loose", "inst_loose"},
		TaskMTBenchEN: {"score", "turn1", "turn2"},
		TaskMTBenchZH: {"score", "turn1", "turn2"},
		TaskGSM8K:     {"acc", "boxed"},
		TaskMATH500:   {"acc", "boxed"},
		TaskCEval:     {"acc"},
		TaskCMMLU:     {"acc"},
	}
	for _, task := range taskOrder {
		present := false
		for _, r := range runs {
			if r.Tasks[task] != nil {
				present = true
			}
		}
		if !present {
			continue
		}
		for i, m := range metricOrder[task] {
			name := ""
			if i == 0 {
				name = task
			}
			fmt.Fprintf(&b, "| %s | %s |", name, m)
			for _, r := range runs {
				ts := r.Tasks[task]
				if ts == nil {
					b.WriteString(" — |")
					continue
				}
				cell := fmt.Sprintf("%.1f", ts.Metrics[m])
				if task == TaskMTBenchEN || task == TaskMTBenchZH {
					cell = fmt.Sprintf("%.2f", ts.Metrics[m])
					if ts.Metrics["judged"] == 0 {
						cell = "未评"
					}
				}
				if i == 0 {
					cell = "**" + cell + "**"
					if ts.NClean < ts.N {
						cell += fmt.Sprintf(" (净 %.1f, n=%d)", ts.Clean[m], ts.NClean)
					}
					if ts.Errors > 0 {
						cell += fmt.Sprintf(" ⚠%d 作废", ts.Errors)
					}
				}
				b.WriteString(" " + cell + " |")
			}
			b.WriteString("\n")
		}
	}
	b.WriteString("\n### 输出统计\n\n| 项 | 指标 |")
	for _, r := range runs {
		b.WriteString(" " + runLabel(r) + " |")
	}
	b.WriteString("\n|---|---|" + strings.Repeat("---:|", len(runs)) + "\n")
	rows := []struct {
		name string
		get  func(*TaskStats) string
	}{
		{"思考闭合", func(s *TaskStats) string { return pctCell(s.ThinkClosed) }},
		{"空思考", func(s *TaskStats) string { return pctCell(s.EmptyThink) }},
		{"思考语言=题目语言", func(s *TaskStats) string { return pctCell(s.ThinkLangMatch) }},
		{"复读(loop)", func(s *TaskStats) string { return pctCell(s.Loop) }},
		{"撞上限", func(s *TaskStats) string { return pctCell(s.HitLimit) }},
		{"思考字数 p50/p90", func(s *TaskStats) string { return fmt.Sprintf("%d / %d", s.ThinkCharsP50, s.ThinkCharsP90) }},
		{"生成 token p50", func(s *TaskStats) string { return fmt.Sprint(s.TokensP50) }},
		{"回答字数 p50", func(s *TaskStats) string { return fmt.Sprint(s.AnswerCharsP50) }},
	}
	for _, task := range taskOrder {
		present := false
		for _, r := range runs {
			if r.Stats[task] != nil {
				present = true
			}
		}
		if !present {
			continue
		}
		for i, row := range rows {
			name := ""
			if i == 0 {
				name = task
			}
			fmt.Fprintf(&b, "| %s | %s |", name, row.name)
			for _, r := range runs {
				if s := r.Stats[task]; s != nil {
					b.WriteString(" " + row.get(s) + " |")
				} else {
					b.WriteString(" — |")
				}
			}
			b.WriteString("\n")
		}
	}
	b.WriteString("\n带历史时的空思考率（turn2 = MT-Bench 第二轮，历史里是 `<think></think>`）：\n\n| 轮次 |")
	for _, r := range runs {
		b.WriteString(" " + runLabel(r) + " |")
	}
	b.WriteString("\n|---|" + strings.Repeat("---:|", len(runs)) + "\n")
	for _, k := range []string{"turn1", "turn2"} {
		fmt.Fprintf(&b, "| %s |", k)
		for _, r := range runs {
			b.WriteString(" " + pctCell(r.History[k]) + " |")
		}
		b.WriteString("\n")
	}
	return b.String()
}

func pctCell(r Rate) string {
	if r.N == 0 {
		return "—"
	}
	return fmt.Sprintf("%.1f%% (%d/%d)", 100*float64(r.K)/float64(r.N), r.K, r.N)
}

// renderFlips compares every run with the first one item by item on the
// binary-verdict tasks: wins/losses and a two-sided sign test.
func renderFlips(dirs []string) (string, error) {
	load := func(dir string) (map[string]Scored, error) {
		rows, err := readJSONL(filepath.Join(dir, "scored.jsonl"))
		if err != nil {
			return nil, err
		}
		out := map[string]Scored{}
		for _, row := range rows {
			data, _ := json.Marshal(row)
			var s Scored
			if err := json.Unmarshal(data, &s); err != nil {
				return nil, err
			}
			out[s.ID] = s
		}
		return out, nil
	}
	base, err := load(dirs[0])
	if err != nil {
		return "", err
	}
	var b strings.Builder
	b.WriteString("\n### 逐题翻转（对第一个 run，只算两边都有结果的题）\n\n| run | 项 | 共同题数 | 赢 | 输 | 符号检验 p |\n|---|---|---:|---:|---:|---:|\n")
	for _, dir := range dirs[1:] {
		other, err := load(dir)
		if err != nil {
			return "", err
		}
		for _, task := range taskOrder {
			if task == TaskMTBenchEN || task == TaskMTBenchZH {
				continue
			}
			n, win, lose := 0, 0, 0
			for id, a := range base {
				o, ok := other[id]
				if a.Task != task || !ok || a.Error != "" || o.Error != "" {
					continue
				}
				n++
				switch {
				case o.Correct && !a.Correct:
					win++
				case a.Correct && !o.Correct:
					lose++
				}
			}
			if n == 0 {
				continue
			}
			fmt.Fprintf(&b, "| %s | %s | %d | +%d | −%d | %.3g |\n", filepath.Base(dir), task, n, win, lose, signTest(win, lose))
		}
	}
	return b.String(), nil
}

// signTest is the exact two-sided binomial test of k wins against l losses.
func signTest(k, l int) float64 {
	n := k + l
	if n == 0 {
		return 1
	}
	small := min(k, l)
	p := 0.0
	for i := 0; i <= small; i++ {
		p += math.Exp(lgammaChoose(n, i) - float64(n)*math.Ln2)
	}
	return math.Min(1, 2*p)
}

func lgammaChoose(n, k int) float64 {
	a, _ := math.Lgamma(float64(n + 1))
	b, _ := math.Lgamma(float64(k + 1))
	c, _ := math.Lgamma(float64(n - k + 1))
	return a - b - c
}
