# 用 harness 渲染训练语料

训练语料不再由 Python 按文档重写 wire，而是把 teacher 动作**回放进真实 eval harness**，
再从 trace 里切出训练行。每条训练行的字节由此与同一 wire 下跑分时模型看到的 prompt
逐字节相同：System 块、工具回执、每步 post-tool 提醒、失败/RECOVERY 提示、重复拒绝、
强制收尾块，全部来自同一份 Go 代码。

背景：`tooling/workv1_wire.py` 按 [corpus-g1k-wire-format.md](corpus-g1k-wire-format.md)
手写拼接，漏掉了 harness 在两次动作之间插入的 User 块（g1k 预设 `usermsg=split` 每次成功
调用后都插 "Use the Tool results above…"），state 只在第 1 步见过训练分布
（见 [state-lr-sweep 复核](evaluations/state-lr-sweep-20260923/REPORT.md) §8）。

## 组成

| 部件 | 作用 |
|---|---|
| `rwkv-cli agent-eval --script <jsonl>` | 用脚本代替模型：按 case ID 依次返回 teacher 输出，不需要端点、不需要 `--model`；其余（wire、工具、打分）照常 |
| `internal/agent/eval/script.go` | 脚本格式、`ScriptGeneratorFactory`；eval 在 context 里带 case ID |
| `internal/agent/eval/corpus.go` + `cmd/tracecorpus` | 从 run 目录切训练行，逐步校验 harness 没有偏离脚本 |
| `scripts/harness_corpus.py` | normalized record 或（题目目录 + 脚本）→ agent-eval → tracecorpus 一条龙 |
| `scripts/trace2script.py` | teacher 跑出的 run → 脚本：筛通过、去重、限每题路径数、参数去默认值 |
| `scripts/decontam.py` | 蒸馏题与测试题的相似度闸门 |

## 用法

```bash
go build -o bin/rwkv-cli ./cmd/rwkv-cli && go build -o bin/tracecorpus ./cmd/tracecorpus
python3 scripts/harness_corpus.py \
  --records datasets/workspace-agent-700-20260920/generated/normalized/all.jsonl \
  --out runs/harness-corpus-700
```

默认 flags 与 `.claude/skills/rwkv-bench/sweep.py` 的 workbank 臂一致（`--tool-catalog work-v1
--file-tools lines --max-steps 16 --max-tokens 4096 --decision-max-tokens 2048 --profile g1k
--strict-spec`）。case 写成 bank 目录（`cases/<id>/case.json`），所以走与 workbank 相同的
suite 分支和默认值（rescue 关、`firstcall=auto`）；`run/run.json` 的 `wire_hash` 应与对应
跑分 run 相同，这是对齐的验收点。换 wire 在 `--` 后追加 agent-eval flags。

产物（`--out` 下，派生数据不入库）：

- `rows.jsonl`：`{text, loss_spans, meta}`，多轮题每轮一行（`meta.turn`）；`loss_spans` 为 Unicode 码点偏移（与
  `workv1_wire.py` 同单位），只覆盖脚本标 `supervised` 的输出；`meta` 带 `wire_hash`、
  `harness_version`、`canonicalized`。当前 state 训练器只读 `text`，转 textonly 时丢掉其余字段即可。
- `rejects.jsonl`：被拒 case 及原因。

## 脚本格式

每行一个 case：`{"case_id": "...", "outputs": [{"text": "...", "supervised": true}, ...]}`。
`text` 是该次生成的原始输出（tool call 写 `<tool_call>{...}</tool_call>`，终答写纯文本），
按生成顺序排列，跨轮连续。`supervised: false` 用于恢复前缀这类只作上下文的动作。

## 拒绝规则（宁拒不修）

- harness 的生成次数 ≠ 脚本输出数（多了重试、提前强制收尾等）；
- 某次生成报错；
- 同一轮内 transcript 不是只追加（`usermsg=rewrite`、历史压缩会触发）；多轮题按轮切行，见下文冒烟一节；
- harness 回写的动作与 teacher 原话不同。唯一放行的差异是 tool call JSON 语义相同、字节不同
  （Go 把 `<`、`>`、`&` 转义为 `\u003c` 等）：训练行采用 harness 字节（模型在历史里看到的就是它），
  计入 `meta.canonicalized`；
- 默认 `--require-pass`：teacher 轨迹在真实打分器下不通过；
- bank 加载器不接受的 case（出题规则，例如 `expect.run` 脚本必须随 files 下发）：由真实加载器
  判定，移到 `unloadable/` 后重试。

## 注意

- 全文 loss 训练器会把 `supervised: false` 的动作一起学进去。在训练器支持 `loss_spans` 之前，
  脚本里不要放"示范犯错"的动作（例如故意的重复调用）；harness 主动给的反馈（工具报错、强制收尾）
  可以放。
- 新增提示块使每行平均多约 250 token（700 条实测 p99 3335、max 3703，仍在 ctx 4096 内）。

## 蒸馏流程：写题目，让 teacher 跑轨迹

```bash
# 1. teacher 在蒸馏题库上跑 k 次（原生通道、温度调高；每次换 --output）
bin/rwkv-cli agent-eval --completion chat-completions --model <teacher> ... \
  --cases bench/distill/cases --tool-catalog work-v1 --file-tools lines --output runs/distill/k0
# 2. 抽路径：通过 + 干净 + 去重 + 每题 ≤2 条，参数去默认值
python3 scripts/trace2script.py --run runs/distill/k0 --run runs/distill/k1 ... \
  --out runs/distill/script.jsonl --report runs/distill/paths.jsonl
# 3. 用 student 的 wire 重放并切行
python3 scripts/harness_corpus.py --cases bench/distill/cases \
  --script runs/distill/script.jsonl --out runs/distill/corpus
```

- `trace2script.py` 只带走动作（工具名、参数、终答），teacher 的 wire、思考和回执全部丢弃，
  重放时由 student 的 harness 重新执行工具。丢弃规则：失败、有协议重试、工具报错或被拒、
  进入强制收尾、终答被 harness 修复过。选路：先取最短，之后只收工具序列不同的，每题最多
  `--max-per-case`（默认 2）。参数等于实现默认值的去掉（teacher 习惯把 schema 字段填满，
  如 `"path":"","max_results":50`）。脚本 case id 为 `<题目id>--p<n>`。
- 输出的 pass@k 分布即出题质检：0/k 的题先查 expect 与题面，再决定是否蒸馏。
- 冒烟（2026-09-24，workbank 上 DeepSeek 3 次，**测试集，仅验证管线**）：189 条路径在 g1k 下
  重放 189/189 通过。最初 2 条被拒（`nt-0010`、`nt-0012`，"第 9 次生成非只追加"）：它们是两轮题，
  第 2 轮开始时 harness 提交的历史不含第 1 轮的 post-tool 提醒，跑分时模型看到的也是这样。
  现在 tracecorpus **按轮切行**：每轮一行，文本止于本轮最后一次输出，只有本轮输出有 loss span，
  前几轮以提交后的历史出现；轮内仍要求只追加，跨轮只要求下一轮 prompt 带着上一轮的最后输出。
  结果 189 个 case → 191 行，原 187 行逐字节不变。

## 测试题与蒸馏题分开

两者目的相反：测试题要**稳定、可区分、冻结**，蒸馏题要**覆盖、多样、量大**。混用会让跑分
虚高——700 条的 36 个种子全部是 workbank 题（anchor 分支就是原题，b/r/v/x 为其变体），
[state-lr-sweep](evaluations/state-lr-sweep-20260923/REPORT.md) 的 workbank 分数因此偏乐观。

| | 测试题（`bench/workbank`） | 蒸馏题（`bench/distill`，另建） |
|---|---|---|
| 目的 | 度量 | 教 |
| 规模 | 小而冻结，版本化 | 大、持续增加 |
| 质量要求 | 答案唯一、判分精确、每题测一个能力点 | expect 正确（错 expect 会滤掉正确路径或放进错误路径）；teacher pass@k 作质检 |
| 来源 | 人工精出题 | 按能力点模板批量出题，**不得以测试题为种子** |
| 覆盖 | 现有 10 类场景 | 另需直答、追问、中文、`data_query`、UNKNOWN 陷阱等 student 缺的行为 |

闸门：

- **来源规则**（主闸）：蒸馏题的种子、模板、fixture 不得来自测试题。改名改数字的同题变体表面
  相似度很低（700 条的 b/v 变体大多查不出），只能靠来源管。
- **`scripts/decontam.py`**（兜底）：按模型可见文本（prompt 5-gram、fixture 行 3-gram 包含度、
  专有名）比对，忽略测试集中 >5% 题目共有的模板片段。校准：700 条 anchor 36/36 命中、
  workbank 内部两两误报 0/148。有命中时退出码 1。
- **`harness_corpus.py` 拒渲染 `bench/workbank`**，除非显式 `--allow-test-bank`（仅冒烟）。

## 700 条首轮结果（2026-09-24）

670/700 渲染成功，与旧渲染逐块 diff：除 harness 插入块（post-tool 提醒 2874 处、失败提示约 50 处）
和 25 处转义规范化外逐字节相同。30 条被拒全是数据与当前 harness 的漂移：700 条于 2026-09-20 在旧
打分语义下验收，09-21 的 scorer v3（`85e7dc6`）把 `expect.run` 的工作目录从 sandbox 改为
`sandbox/workspace`、把 hidden file 限制在工作区内，数据未随之重验：

| 问题 | 条数 | id |
|---|---|---|
| `expect.run` 参数写 `workspace`（旧 cwd 下的相对路径），现 cwd 即工作区，应为 `.` | 10 | `ws7-cfg-0001-b30..b33`、`ws7-cfg-0002-b30..b33`、`ws7-cfg-0003-b30`、`ws7-cfg-0003-b33` |
| hidden file 放在工作区外（旧布局），现被拒 | 4 | `ws7-scr-0001..0004-x10` |
| teacher 脚本输出依赖目录遍历顺序（未排序），在当前沙箱里顺序与验收时不同 | 4 | `ws7-scr-0001-r10/r11/r20/r21` |
| `expect.run` 脚本由 teacher 新建、不在初始 files（bank 出题规则不收） | 12 | `ws7-scr-0001-v20`、`ws7-scr-0002-v20`、`ws7-scr-0003-b30..b33/v20`、`ws7-scr-0004-b30..b33/v20` |

前三类是修数据即可救回的（改参数/路径、脚本里加 `sorted()`）；最后一类需要决定是否放宽 bank
规则或给 case 补参考脚本。
