package exam

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// Coverage floors behind the automatic gap list in SUITES.md: a task kind
// needs this many cases per language, a difficulty factor this many cases.
const (
	gapTaskPerLanguage = 10
	gapDifficulty      = 15
)

// RenderSuites writes SUITES.md, the human side of the manifests. It is
// generated so the table can never disagree with the JSON.
func (exam *Exam) RenderSuites() string {
	var b strings.Builder
	w := func(format string, args ...any) { fmt.Fprintf(&b, format, args...) }

	w("# 题库总表\n\n")
	w("> 本文件由 `rwkv-lab exam build` 根据 `bench/exam/*.json` 自动生成，**不要手改**。\n")
	w("> 改题之后重新运行 `go run ./cmd/rwkv-lab exam build`；`exam build --check` 和 `exam lint` 会挡住没重建的改动。\n\n")

	w("## 怎么跑\n\n")
	w("```bash\n./local/bin/rwkv-cli agent-eval --profile g1k --strict-spec --cases bench/exam/quick.json --harness app ...\n```\n\n")
	w("- `--cases` 可以直接指向下面任意一个 JSON 清单；题目文件留在各自原来的目录，清单只记路径和内容哈希。\n")
	w("- 清单哈希相同的两次跑分才能直接比。题目改过、清单重建过，哈希就会变。\n\n")

	w("## 考卷\n\n")
	w("| 考卷 | 题数 | 哈希 | 用途 | 清单 |\n|---|---|---|---|---|\n")
	w("| exam-full | %d | `%s` | %s | `bench/exam/full.json` |\n", len(exam.Full.Cases), exam.Full.Hash[:12], exam.Full.Description)
	if exam.Quick != nil {
		w("| exam-quick | %d | `%s` | %s | `bench/exam/quick.json` |\n", len(exam.Quick.Cases), exam.Quick.Hash[:12], exam.Quick.Description)
	}
	w("\n")

	w("## 名词\n\n")
	w("每道题有一个**任务类型**（用户想让 App 做什么）和零到多个**难点**（这道题难在哪）。\n\n")
	w("| 任务类型 | 意思 |\n|---|---|\n")
	for _, id := range TaskOrder {
		w("| `%s` | %s |\n", id, TaskLabel[id])
	}
	w("\n| 难点 | 意思 |\n|---|---|\n")
	for _, id := range DifficultyOrder {
		w("| `%s` | %s |\n", id, DifficultyLabel[id])
	}
	w("\n| 判分方式 | 意思 |\n|---|---|\n")
	for _, id := range []string{FormNumber, FormExact, FormContains, FormAbstain, FormNoCall, FormFile} {
		w("| `%s` | %s |\n", id, FormLabel[id])
	}
	w("\n")

	exam.renderComposition(&b, "exam-full", exam.Full.Cases)
	if exam.Quick != nil {
		exam.renderComposition(&b, "exam-quick", exam.Quick.Cases)
	}

	w("## 来源题集\n\n")
	w("题目按出处放在不同目录。每个来源也有一份同格式的清单 `bench/exam/suites/<名字>.json`，按原来的工具清单仍可单独跑。\n\n")
	w("| 来源 | 目录 | 内容 | 原工具清单 | 题数 | 泄漏 | 排除 | 进完整考卷 |\n|---|---|---|---|---|---|---|---|\n")
	inFull := map[string]int{}
	for _, row := range exam.Full.Cases {
		inFull[row.Suite]++
	}
	for _, source := range Sources {
		items := exam.Suites[source.Name]
		leaked, excluded := 0, 0
		for _, item := range items {
			if item.Row.Leaked {
				leaked++
			} else if _, ok := exam.Exclude[item.Row.ID]; ok {
				excluded++
			}
		}
		catalog := source.ToolCatalog
		if catalog == "" {
			catalog = "内置"
		}
		w("| %s | `%s` | %s | %s | %d | %d | %d | %d |\n",
			source.Label, source.Dir, source.Purpose, catalog, len(items), leaked, excluded, inFull[source.Name])
	}
	w("\n- **泄漏**：题目内容进过训练集（`bench/workbank/seeded-base700.txt`），不进考卷，只保留在来源清单里供历史对照。\n")
	w("- **排除**：`bench/exam/exclude.txt` 里登记的题，原因如下。\n\n")
	if len(exam.Exclude) > 0 {
		ids := make([]string, 0, len(exam.Exclude))
		for id := range exam.Exclude {
			ids = append(ids, id)
		}
		sort.Strings(ids)
		w("| 题目 | 排除原因 |\n|---|---|\n")
		for _, id := range ids {
			w("| `%s` | %s |\n", id, exam.Exclude[id])
		}
		w("\n")
	}

	w("## 覆盖缺口（自动检查）\n\n")
	gaps := exam.Gaps()
	if len(gaps) == 0 {
		w("没有低于下限的格子。\n")
	} else {
		w("下限：每种任务类型每种语言至少 %d 题，每种难点至少 %d 题。低于下限的是补题优先级：\n\n", gapTaskPerLanguage, gapDifficulty)
		for _, gap := range gaps {
			w("- %s\n", gap)
		}
	}
	return b.String()
}

// Gaps lists the coverage cells of the full exam below the floors.
func (exam *Exam) Gaps() []string {
	var gaps []string
	counts := map[string]map[string]int{}
	diffs := map[string]int{}
	for _, row := range exam.Full.Cases {
		if counts[row.Task] == nil {
			counts[row.Task] = map[string]int{}
		}
		counts[row.Task][row.Language]++
		for _, item := range row.Difficulties {
			diffs[item]++
		}
	}
	for _, task := range TaskOrder {
		for _, language := range []string{"zh", "en"} {
			if n := counts[task][language]; n < gapTaskPerLanguage {
				gaps = append(gaps, fmt.Sprintf("%s · %s：%d 题（差 %d）", TaskLabel[task], languageLabel(language), n, gapTaskPerLanguage-n))
			}
		}
	}
	for _, item := range DifficultyOrder {
		if n := diffs[item]; n < gapDifficulty {
			gaps = append(gaps, fmt.Sprintf("难点「%s」：%d 题（差 %d）", DifficultyLabel[item], n, gapDifficulty-n))
		}
	}
	return gaps
}

func languageLabel(language string) string {
	if language == "zh" {
		return "中文"
	}
	return "英文"
}

func (exam *Exam) renderComposition(b *strings.Builder, name string, rows []eval.ExamCase) {
	w := func(format string, args ...any) { fmt.Fprintf(b, format, args...) }
	var summary Summary
	if name == "exam-quick" && exam.Quick != nil {
		_ = json.Unmarshal(exam.Quick.Summary, &summary)
	} else {
		_ = json.Unmarshal(exam.Full.Summary, &summary)
	}
	w("## %s 的构成（%d 题）\n\n", name, len(rows))
	w("| 任务类型 | 中文 | 英文 | 合计 |\n|---|---|---|---|\n")
	for _, task := range TaskOrder {
		zh, en := summary.TaskByLanguage[task]["zh"], summary.TaskByLanguage[task]["en"]
		w("| %s | %d | %d | %d |\n", TaskLabel[task], zh, en, zh+en)
	}
	w("| **合计** | %d | %d | %d |\n\n", summary.ByLanguage["zh"], summary.ByLanguage["en"], summary.Total)

	w("| 难点 | 题数 |\n|---|---|\n")
	for _, item := range DifficultyOrder {
		w("| %s | %d |\n", DifficultyLabel[item], summary.ByDifficulty[item])
	}
	w("| 没有标难点 | %d |\n\n", summary.ByDifficulty["none"])

	w("| 判分方式 | 题数 |\n|---|---|\n")
	for _, form := range []string{FormNumber, FormExact, FormContains, FormAbstain, FormNoCall, FormFile} {
		if n := summary.ByAnswerForm[form]; n > 0 {
			w("| %s | %d |\n", FormLabel[form], n)
		}
	}
	w("\n| 来源 | 题数 |\n|---|---|\n")
	for _, source := range Sources {
		if n := summary.BySuite[source.Name]; n > 0 {
			w("| %s | %d |\n", source.Label, n)
		}
	}
	w("\n")
}
