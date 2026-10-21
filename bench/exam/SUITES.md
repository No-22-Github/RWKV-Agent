# 题库总表

> 本文件由 `rwkv-lab exam build` 根据 `bench/exam/*.json` 自动生成，**不要手改**。
> 改题之后运行 `go run ./cmd/rwkv-lab exam build`；`exam build --check` 和 `exam lint` 会拦下没有重建的改动。
> 设计和来由：`docs/evaluations/bench-composition-20261015/REPORT.md` §8～§10。

## 这是什么

考卷考的是**用户在 RWKV Agent App 里真实会做的事**，并且按 **App 新建连接的默认配置**来考：
agent-wire-v1.0 对话格式（原名 g1k）；文件、编辑、计算、web、天气、bash 工具全开；改文件先进「暂存」（只在内存里，用户点确认才写盘，评测跑完自动当作已确认）；
同一个工具连调 3 次会触发「复读兜底」（App 强制模型收尾作答）。评测和 App 用的是同一份组装代码（`internal/agent/product`），所以分数就是用户在 App 里能得到的效果。

## 怎么跑

```bash
go build -o local/bin/rwkv-cli ./cmd/rwkv-cli
RWKV_JUSTBASH_SIDECAR=$PWD/local/bin/justbash-sidecar ./local/bin/rwkv-cli agent-eval \
  --completion rwkv-lightning-cuda --model <模型 id> --api-url <端点>/v1 \
  --profile agent-wire-v1.0 --strict-spec --sampling agent-default --state-id <state> \
  --cases bench/exam/quick.json --case-parallelism 48 --output local/runs/<日期>/<名字>
```

- `--cases <清单>`：清单自带工具清单（agent-tool-v2.0）和 `--harness app`（按 App 配置考），预算、兜底等不用再给，给了也不生效。
- `--profile agent-wire-v1.0 --strict-spec`：用 agent-wire-v1.0 对话格式（原名 g1k），并确认它是登记过的预设。API 模型（DeepSeek 等）不传这两个，改传 `--chat-thinking disabled`（App 新建 chat 连接的默认）。
- 暂存文件靠 just-bash sidecar（`scripts/build-justbash.sh` 构建）。完整检查单见 `.claude/skills/rwkv-bench/SKILL.md`。
- 出能力面板：`go run ./cmd/rwkv-lab exam panel <跑分目录>…`。
- 清单记录每题的内容哈希；**清单哈希相同的两次跑分才能直接比**。

## 考卷

| 考卷 | 题数 | 哈希 | 用途 | 清单 |
|---|---|---|---|---|
| agent-exam-v1.0 | 568 | `c5ae05fc103d` | 完整考卷：按 App 默认配置（agent-wire-v1.0，原名 g1k；工具全开、暂存文件、复读兜底）考用户在 App 里会做的事 | `bench/exam/full.json` |
| agent-exam-quick-v1.0 | 76 | `4f8780546009` | 快测版：从完整考卷分层抽出，几分钟跑完，用于快速比较 | `bench/exam/quick.json` |

agent-exam-quick 一定是 agent-exam 的子集：按「任务类型 × 语言」分层，优先选 RWKV 历史上时对时错的题，每类留一道送分题和一道难题，每个来源至少 12%。名单在 `bench/exam/quick-ids.txt`（`rwkv-lab exam select-quick` 生成，每题后面注明入选原因）。

## 考卷版本历史

主版本号：题目集合变了（增删题）。次版本号：题目集合不变，只修订题面或判据。两种情况 `hash` 都会变，比较跑分时仍以 `hash` 为准。
版本表在 `bench/exam/versions.json`（人工维护）；当前题集的 hash 不在表里时，`rwkv-lab exam build` 会拒绝生成，由人判断该升主版本还是次版本。

### agent-exam

| 版本 | 题数 | 哈希 | 起始日期 | 说明 |
|---|---|---|---|---|
| v1.0 | 568 | `c5ae05fc103d` | 2026-10-16 | 568 题：改题面 + Sonnet 补题 190 道后的版本，10-17 起所有考卷跑分都用它 |

### agent-exam-quick

| 版本 | 题数 | 哈希 | 起始日期 | 说明 |
|---|---|---|---|---|
| v1.0 | 76 | `4f8780546009` | 2026-10-16 | agent-exam-v1.0 的分层子集 |

## 怎么解读分数

- **看能力面板，不要只看总分。** 总分会被个别类别左右。
- **单次跑分波动很大。** 2026-10-15 同一配置跑两次，RWKV 在没改过的题上有 21% 翻转。比较两个模型或 checkpoint 要跑 3 次，差距小于同配置 3 次的极差就是「无法区分」。
- 快测版的比例偏高（它专挑有区分度的题），只用来比较，不当作绝对水平。
- 验收成绩和判分复核见 `docs/evaluations/bench-composition-20261015/REPORT.md` §10 与 `review.md`。

## 名词

每道题有一个**任务类型**（用户想让 App 做什么）和零到多个**难点**（这道题难在哪）。

| 任务类型 | 意思 |
|---|---|
| `answer-direct` | 直接回答（不该调工具 / 该先反问） |
| `find-read` | 查找与阅读本地文件 |
| `compute` | 统计与计算 |
| `write` | 改文件与写产物 |
| `external` | 外部信息（上网、天气） |

| 难点 | 意思 |
|---|---|
| `multi-source` | 多个来源拼答案 |
| `check` | 核对与守约束（版本冲突、数据里的指令、只读） |
| `recovery` | 出错恢复（路径不对、链接失效、工具报错） |
| `long-input` | 长输入（大文件、截断、分页） |
| `follow-up` | 用户追问（不止一条用户消息） |
| `decoy` | 有相似的干扰答案 |

一道题可以有多个难点，所以难点的题数加起来会超过总题数；「没有标难点」只表示没匹配到已登记的陷阱，**不等于简单**。

| 判分方式 | 意思 |
|---|---|
| `number` | 回答里出现正确数字就算对（允许误差），不检查有没有同时提到干扰值 |
| `exact` | 整句精确相等（旧判法，考卷里应为 0） |
| `contains` | 回答里按词边界出现正确值就算对；部分题还要求结论写在第一行 |
| `abstain` | 应点名缺的是什么，并说明没有 / 做不到 |
| `no-call` | 这一轮不许调工具，直接回答 |
| `file` | 只看文件最后的样子（评测跑完自动确认暂存改动后检查） |
| `format` | 检查回答的格式（合法 JSON、Markdown 表格、指定语言），可另加内容检查 |

| 来源题集 | 一句话 |
|---|---|
| workbank | 原主考卷，148 道英文工作区任务；其中 36 道进过训练数据（泄漏），不进考卷 |
| p13 | 60 道留存题，专门不给训练用，中文为主 |
| bfcl-product | 由外部基准 BFCL 改写：该不该调工具、缺信息先反问、两轮对话 |
| boundary | 改自社区 primitive-bench 的早期边界题 |
| bash / 天气探针 | 专测 bash 和 get_weather 的题；「第二部分」来自第 14 批出题 |
| agent-tool-v1.0 / v2.0 / v3.1 | 工具清单版本（旧名 work-v1/v2/v3，仍可在命令和清单里使用）。主版本号变了说明模型看到的工具描述或参数变了，小版本号变了说明只改了工具行为。v2.0 比 v1.0 多 bash 和 get_weather；v3 是现在 App 用的清单。考卷清单记的是 v2.0，历史分数都在 v2.0 下跑出来 |

## agent-exam-v1.0 的构成（568 题）

| 任务类型 | 中文 | 英文 | 合计 |
|---|---|---|---|
| 直接回答（不该调工具 / 该先反问） | 47 | 44 | 91 |
| 查找与阅读本地文件 | 73 | 66 | 139 |
| 统计与计算 | 54 | 66 | 120 |
| 改文件与写产物 | 60 | 65 | 125 |
| 外部信息（上网、天气） | 50 | 43 | 93 |
| **合计** | 284 | 284 | 568 |

| 难点 | 题数 |
|---|---|
| 多个来源拼答案 | 74 |
| 核对与守约束（版本冲突、数据里的指令、只读） | 142 |
| 出错恢复（路径不对、链接失效、工具报错） | 48 |
| 长输入（大文件、截断、分页） | 51 |
| 用户追问（不止一条用户消息） | 96 |
| 有相似的干扰答案 | 123 |
| 没有标难点 | 210 |

| 判分方式 | 题数 |
|---|---|
| 回答里出现正确数字就算对（允许误差），不检查有没有同时提到干扰值 | 114 |
| 回答里按词边界出现正确值就算对；部分题还要求结论写在第一行 | 269 |
| 应点名缺的是什么，并说明没有 / 做不到 | 31 |
| 这一轮不许调工具，直接回答 | 23 |
| 只看文件最后的样子（评测跑完自动确认暂存改动后检查） | 110 |
| 检查回答的格式（合法 JSON、Markdown 表格、指定语言），可另加内容检查 | 21 |

| 来源 | 题数 |
|---|---|
| workbank | 111 |
| p13 留存题 | 59 |
| bfcl-product | 60 |
| boundary | 18 |
| bash 探针·老题 | 26 |
| bash 探针·第二部分 | 60 |
| 天气探针·老题 | 14 |
| 天气探针·第二部分 | 30 |
| 考卷补题 | 190 |

## agent-exam-quick-v1.0 的构成（76 题）

| 任务类型 | 中文 | 英文 | 合计 |
|---|---|---|---|
| 直接回答（不该调工具 / 该先反问） | 7 | 7 | 14 |
| 查找与阅读本地文件 | 7 | 10 | 17 |
| 统计与计算 | 8 | 8 | 16 |
| 改文件与写产物 | 7 | 7 | 14 |
| 外部信息（上网、天气） | 8 | 7 | 15 |
| **合计** | 37 | 39 | 76 |

| 难点 | 题数 |
|---|---|
| 多个来源拼答案 | 6 |
| 核对与守约束（版本冲突、数据里的指令、只读） | 14 |
| 出错恢复（路径不对、链接失效、工具报错） | 6 |
| 长输入（大文件、截断、分页） | 6 |
| 用户追问（不止一条用户消息） | 9 |
| 有相似的干扰答案 | 14 |
| 没有标难点 | 34 |

| 判分方式 | 题数 |
|---|---|
| 回答里出现正确数字就算对（允许误差），不检查有没有同时提到干扰值 | 9 |
| 回答里按词边界出现正确值就算对；部分题还要求结论写在第一行 | 49 |
| 应点名缺的是什么，并说明没有 / 做不到 | 2 |
| 这一轮不许调工具，直接回答 | 4 |
| 只看文件最后的样子（评测跑完自动确认暂存改动后检查） | 12 |

| 来源 | 题数 |
|---|---|
| workbank | 16 |
| p13 留存题 | 11 |
| bfcl-product | 11 |
| boundary | 4 |
| bash 探针·老题 | 13 |
| bash 探针·第二部分 | 10 |
| 天气探针·老题 | 6 |
| 天气探针·第二部分 | 5 |

## 来源题集

题目按出处放在不同目录。每个来源也有一份同格式的清单 `bench/exam/suites/<名字>.json`，按原来的工具清单仍可单独跑。

| 来源 | 目录 | 内容 | 原工具清单 | 题数 | 泄漏 | 排除 | 进完整考卷 |
|---|---|---|---|---|---|---|---|
| workbank | `bench/workbank/cases` | 原主考卷：模拟工作区里的日常任务（查表、看日志、改配置、写脚本、上网查） | agent-tool-v1.0 | 148 | 36 | 1 | 111 |
| p13 留存题 | `bench/holdout/p13` | 从未进过训练的留存题，中文为主 | agent-tool-v1.0 | 60 | 0 | 1 | 59 |
| bfcl-product | `bench/exam/imported/bfcl-product` | 工具时机：该不该调工具、缺信息先反问、两轮对话（改写自 BFCL v4） | 内置 | 60 | 0 | 0 | 60 |
| boundary | `bench/exam/imported/boundary` | 早期边界题：多步工具、金融算术、注入（改写自 primitive-bench） | 内置 | 18 | 0 | 0 | 18 |
| bash 探针·老题 | `bench/bashprobe/cases` | 会不会用 bash 做聚合、批量编辑、出错恢复 | agent-tool-v2.0 | 26 | 0 | 0 | 26 |
| bash 探针·第二部分 | `bench/bashprobe/cases-b14` | 第 14 批题转来的 bash 场景题，中英各半 | agent-tool-v2.0 | 60 | 0 | 0 | 60 |
| 天气探针·老题 | `bench/weatherprobe/cases` | 会不会用 get_weather、查完写产物 | agent-tool-v2.0 | 14 | 0 | 0 | 14 |
| 天气探针·第二部分 | `bench/weatherprobe/cases-b14` | 第 14 批题转来的天气场景题 | agent-tool-v2.0 | 30 | 0 | 0 | 30 |
| 考卷补题 | `bench/exam/cases` | 按覆盖缺口新出的题（docs/evaluations/bench-composition-20261015/gap-fill-spec.md） | agent-tool-v2.0 | 190 | 0 | 0 | 190 |

进完整考卷 = 题数 − 泄漏 − 排除。

- **泄漏**：题目内容进过训练集（`bench/workbank/seeded-base700.txt`），不进考卷，只保留在来源清单里供历史对照。
- **排除**：`bench/exam/exclude.txt` 里登记的题（原因见下表）。
- **考卷补题**：按 `docs/evaluations/bench-composition-20261015/gap-fill-spec.md` 新出的题放在 `bench/exam/cases/`，题数为 0 表示还没开始补。

| 题目 | 排除原因 |
|---|---|
| `nt-0011` | 题意过时：原来考「删除做不到」，App 现在有 bash 能删文件；删除类任务按 gap-fill-spec G1 重出 |
| `nt-8001` | 题意过时：同 nt-0011（p13 的中文版） |

## 覆盖缺口（自动检查）

下限是每种任务类型每种语言至少 10 题、每种难点至少 15 题，目前没有低于下限的格子。
下限只是「不至于测不出来」的底线；补题的目标数更高，见 `docs/evaluations/bench-composition-20261015/gap-fill-spec.md`。
