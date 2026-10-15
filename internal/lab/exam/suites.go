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
	w("> 改题之后运行 `go run ./cmd/rwkv-lab exam build`；`exam build --check` 和 `exam lint` 会拦下没有重建的改动。\n")
	w("> 设计和来由：`docs/evaluations/bench-composition-20261015/REPORT.md` §8～§10。\n\n")

	w("## 这是什么\n\n")
	w("考卷考的是**用户在 RWKV Agent App 里真实会做的事**，并且按 **App 新建连接的默认配置**来考：\n")
	w("g1k 对话格式；文件、编辑、计算、web、天气、bash 工具全开；改文件先进「暂存」（只在内存里，用户点确认才写盘，评测跑完自动当作已确认）；\n")
	w("同一个工具连调 3 次会触发「复读兜底」（App 强制模型收尾作答）。评测和 App 用的是同一份组装代码（`internal/agent/product`），所以分数就是用户在 App 里能得到的效果。\n\n")

	w("## 怎么跑\n\n")
	w("```bash\n")
	w("go build -o local/bin/rwkv-cli ./cmd/rwkv-cli\n")
	w("RWKV_JUSTBASH_SIDECAR=$PWD/local/bin/justbash-sidecar ./local/bin/rwkv-cli agent-eval \\\n")
	w("  --completion rwkv-lightning-cuda --model <模型 id> --api-url <端点>/v1 \\\n")
	w("  --profile g1k --strict-spec --sampling g1k-agent --state-id <state> \\\n")
	w("  --cases bench/exam/quick.json --case-parallelism 48 --output local/runs/<日期>/<名字>\n")
	w("```\n\n")
	w("- `--cases <清单>`：清单自带工具清单（work-v2）和 `--harness app`（按 App 配置考），预算、兜底等不用再给，给了也不生效。\n")
	w("- `--profile g1k --strict-spec`：用 g1k 对话格式，并确认它是登记过的预设。API 模型（DeepSeek 等）不传这两个，改传 `--chat-thinking disabled`（App 新建 chat 连接的默认）。\n")
	w("- 暂存文件靠 just-bash sidecar（`scripts/build-justbash.sh` 构建）。完整检查单见 `.claude/skills/rwkv-bench/SKILL.md`。\n")
	w("- 出能力面板：`go run ./cmd/rwkv-lab exam panel <跑分目录>…`。\n")
	w("- 清单记录每题的内容哈希；**清单哈希相同的两次跑分才能直接比**。\n\n")

	w("## 考卷\n\n")
	w("| 考卷 | 题数 | 哈希 | 用途 | 清单 |\n|---|---|---|---|---|\n")
	w("| exam-full | %d | `%s` | %s | `bench/exam/full.json` |\n", len(exam.Full.Cases), exam.Full.Hash[:12], exam.Full.Description)
	if exam.Quick != nil {
		w("| exam-quick | %d | `%s` | %s | `bench/exam/quick.json` |\n", len(exam.Quick.Cases), exam.Quick.Hash[:12], exam.Quick.Description)
	}
	w("\nexam-quick 一定是 exam-full 的子集：按「任务类型 × 语言」分层，优先选 RWKV 历史上时对时错的题，每类留一道送分题和一道难题，每个来源至少 12%%。")
	w("名单在 `bench/exam/quick-ids.txt`（`rwkv-lab exam select-quick` 生成，每题后面注明入选原因）。\n\n")

	w("## 怎么解读分数\n\n")
	w("- **看能力面板，不要只看总分。** 总分会被个别类别左右。\n")
	w("- **单次跑分波动很大。** 2026-10-15 同一配置跑两次，RWKV 在没改过的题上有 21%% 翻转。比较两个模型或 checkpoint 要跑 3 次，差距小于同配置 3 次的极差就是「无法区分」。\n")
	w("- 快测版的比例偏高（它专挑有区分度的题），只用来比较，不当作绝对水平。\n")
	w("- 验收成绩和判分复核见 `docs/evaluations/bench-composition-20261015/REPORT.md` §10 与 `review.md`。\n\n")

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
	w("\n一道题可以有多个难点，所以难点的题数加起来会超过总题数；「没有标难点」只表示没匹配到已登记的陷阱，**不等于简单**。\n\n")
	w("| 判分方式 | 意思 |\n|---|---|\n")
	for _, id := range []string{FormNumber, FormExact, FormContains, FormAbstain, FormNoCall, FormFile, FormFormat} {
		w("| `%s` | %s |\n", id, FormLabel[id])
	}
	w("\n| 来源题集 | 一句话 |\n|---|---|\n")
	w("| workbank | 原主考卷，148 道英文工作区任务；其中 36 道进过训练数据（泄漏），不进考卷 |\n")
	w("| p13 | 60 道留存题，专门不给训练用，中文为主 |\n")
	w("| bfcl-product | 由外部基准 BFCL 改写：该不该调工具、缺信息先反问、两轮对话 |\n")
	w("| boundary | 改自社区 primitive-bench 的早期边界题 |\n")
	w("| bash / 天气探针 | 专测 bash 和 get_weather 的题；「第二部分」来自第 14 批出题 |\n")
	w("| work-v1 / work-v2 | 旧的工具清单版本；v2 比 v1 多 bash 和 get_weather。考卷统一用 App 的清单（等同 work-v2） |\n\n")

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
	w("\n进完整考卷 = 题数 − 泄漏 − 排除。\n\n")
	w("- **泄漏**：题目内容进过训练集（`bench/workbank/seeded-base700.txt`），不进考卷，只保留在来源清单里供历史对照。\n")
	w("- **排除**：`bench/exam/exclude.txt` 里登记的题（原因见下表）。\n")
	w("- **考卷补题**：按 `docs/evaluations/bench-composition-20261015/gap-fill-spec.md` 新出的题放在 `bench/exam/cases/`，题数为 0 表示还没开始补。\n\n")
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
		w("下限是每种任务类型每种语言至少 %d 题、每种难点至少 %d 题，目前没有低于下限的格子。\n", gapTaskPerLanguage, gapDifficulty)
		w("下限只是「不至于测不出来」的底线；补题的目标数更高，见 `docs/evaluations/bench-composition-20261015/gap-fill-spec.md`。\n")
	} else {
		w("下限：每种任务类型每种语言至少 %d 题，每种难点至少 %d 题。低于下限的格子（补题目标更高，见 gap-fill-spec.md）：\n\n", gapTaskPerLanguage, gapDifficulty)
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
	for _, form := range []string{FormNumber, FormExact, FormContains, FormAbstain, FormNoCall, FormFile, FormFormat} {
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
