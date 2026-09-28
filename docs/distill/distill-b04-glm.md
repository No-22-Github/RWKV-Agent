# b04 蒸馏批次（GLM）—— 执行规格

> 读者：zcode 里的**主控 Agent**，以及它派出的**解题子 Agent**（读 §2、§4 的简报）和**出题子 Agent**（读 §3、§4 的简报）。
> 本文是 [`distill-workflow.md`](distill-workflow.md) 的覆盖层，没写到的以那份为准。能做多少做多少，按 §1 的波次顺序推进。

## 0. 做什么

子 Agent 扮演 student 模型，用 `bench/distill/tools/step.py` 在真实 harness 里一步一步做题：工具由 harness 真实执行，子 Agent 只看到模型会看到的 prompt。
做完的题由 `collect.py` 收成 `bench/distill/scripts/b04.jsonl`，再交给 `corpus render` 生成训练行。

**干净比数量重要**：宁可少做，不要放宽任何一条标准。

不做：不跑 `agent-eval --completion chat-completions`；不走 records 模式；不用 `no_tool` 工具作答；不改 Go 代码、不改旧题、不整理仓库；不训练、不跑分。

## 1. 波次（按顺序做）

| 波次 | 内容 | 题数 |
|---|---|---|
| **W0** | 重解 `bench/distill/tools/w0-cases.tsv` 里的旧 notool 题，**零调用**作答（beyond_capability 允许先查工作区再拒绝） | 117 |
| **W1** | 出新题并解：多轮 | 60 |
| **W2** | 出新题并解：tabular / logs 短路径、TR-ABSENT 成对 | 90 |

W1 配额：

| scenario / task_type | 题数 | 形状 |
|---|---|---|
| hybrid / multi_turn，带 TR-AMBIG | 20 | 第 1 轮可以先查工作区，发现多个候选后反问；第 2 轮用户澄清，按数值/字符串题作答 |
| notool / ambiguous_request | 15 | 第 1 轮零调用反问；第 2 轮澄清后零调用作答 |
| hybrid / multi_turn，追问型（不带 TR-AMBIG） | 25 | 第 1 轮是正常工具题；第 2 轮就同一工作区追问（"那 10 月呢？"），证据够就直接答，不够最多再调 1 次 |

W2 配额：

| scenario / task_type | 题数 | 要求 |
|---|---|---|
| tabular（aggregate / filter_count / rank / reconcile） | 35 | L0/L1，`ref_calls` ≤ 3；其中 ≥ 15 题主表 ≥ 40 行 |
| logs（count_events / locate_error / time_window） | 35 | L0/L1，`ref_calls` ≤ 3；其中 ≥ 10 题日志 ≥ 80 行 |
| TR-ABSENT 成对（config / docs，各 5 族 × 2 题） | 20 | 同族两题：一题答案存在，一题信息缺失、期望 `UNKNOWN` |

**出题的和解题的必须是不同的子 Agent 会话。** 同一题不得同时派给两个解题子 Agent。

## 2. 解题协议（给解题子 Agent）

你扮演一个本地 Agent 模型。`step.py` 打印的内容就是模型此刻能看到的全部；你每次写的一段文本就是模型的**一次完整输出**，会逐字节进入训练数据。

**禁读**：`bench/distill/cases/` 下任何文件（只能把目录路径交给 step.py）、`bench/distill/scripts/`、`bench/workbank/`、`runs/`。

**命令**（仓库根目录；`<dir>` 形如 `bench/distill/cases/notool/nt-5010`）：

```bash
python3 bench/distill/tools/step.py show <dir>     # 第一次：打印完整 prompt
python3 bench/distill/tools/step.py add <dir> - <<'EOF'
<tool_call>{"name":"read_file","arguments":{"path":"ops/rota.csv"}}</tool_call>
EOF
python3 bench/distill/tools/step.py undo <dir>     # 撤销上一步，只用于修自己写坏的格式
```

- 一律用 `add <dir> -` 加带引号的 heredoc（`<<'EOF'`）传文本，不要把 JSON 放在命令行参数里。
- 出现 `CASE FINISHED: PASS/FAIL` 就结束该题。**FAIL 不重试、不删状态文件**，在 `runs/distill/b04/triage.tsv` 追加一行 `<case_id>\tFAIL\t<一句话原因>`。

**输出格式：**

| 类型 | 正确 | 错误 |
|---|---|---|
| 工具调用 | 恰好一个 `<tool_call>{"name":"…","arguments":{…}}</tool_call>`，紧凑 JSON，前后无任何文字 | 前面加说明 / 一次两个调用 / 代码块包裹 |
| 终答（题面有 `Reply with only the final answer`） | 只有答案：`298`、`telemetry/gateway.yaml`、`UNKNOWN` | `298 crates` / `The answer is 298.` / `**298**` / 答案后再接任何内容 |
| 普通回答、解释 | 纯文本 1–4 句 | Markdown 标题、表格、加粗、emoji |
| 反问 | 一句话，点名候选项，问号结尾：`The log has two Ridgeway blocks, Ridgeway North and Ridgeway South. Which one do you mean?` | 反问的同时先给答案 |
| 拒绝 | 1–2 句：做不到什么 + 为什么 + 能替你做什么；含 can't / cannot / unable | 只答 `UNKNOWN` |

**行为规则：**

1. notool 题（beyond_capability 除外）第 1 步就作答，不调用任何工具，包括 `calculator`。
2. 工具题走最短路径：不知道文件在哪先 `list_files`，知道就直接读；大表用 `data_query` 聚合。
3. 不重复成功过的调用。
4. 证据够了立刻作答。
5. 题面给了 UNKNOWN 契约时，找过两三个合理位置都没有就答 `UNKNOWN`。
6. 不写 `<think>`，不复述工具回执，不写 `Assistant:` / `User:` 之类角色标签。

## 3. 出题（给出题子 Agent）

### 3.1 必读材料（按顺序读）

| # | 文档 | 读什么 |
|---|---|---|
| 1 | [`bench/workbank/docs/drafting-brief.md`](../../bench/workbank/docs/drafting-brief.md) | workbank 测试题当初给 GLM 起草 Agent 的简报：12 条硬规则、schema 要点、工具行为速查、自检闭环。**先读这份**，但它是给测试题写的，与蒸馏题冲突处见下方「覆盖」 |
| 2 | [`bench/workbank/docs/authoring-guide.md`](../../bench/workbank/docs/authoring-guide.md) | 出题手册（最高权威）：题型 §2、陷阱目录 §3、难度 §4、tag 词表 §5、表面多样性 §6、NOTES 格式 §7、**反例库 §8（X-001～X-012，都是真实翻过车的）** |
| 3 | [`bench/workbank/docs/HANDOFF.md`](../../bench/workbank/docs/HANDOFF.md) §2 | `case.json` schema v5 字段契约与完整样例 |
| 4 | [`bench/workbank/docs/M0-findings.md`](../../bench/workbank/docs/M0-findings.md) §1/§2/§9 | 工具真实行为（`data_query` 不解析 `$1,234.50`、`read_file` 64KB 截断等） |
| 5 | [`bench/workbank/docs/tag-vocab.json`](../../bench/workbank/docs/tag-vocab.json) | 场景、task_type、陷阱、禁词的机器可读枚举（只读引用，不复制） |
| 6 | [`docs/distill/distill-workflow.md`](distill-workflow.md) §2 | 蒸馏题与测试题的差异：来源禁读表 §2.1、ID/canary §2.2、差异表 §2.3、完整样例 §2.5、出题坑 §2.6 |
| 7 | [`docs/evaluations/distill-audit-20260926/REPORT.md`](../evaluations/distill-audit-20260926/REPORT.md) §2 | 上一轮题库审计发现的问题：判据 fail-open、stable_fact 实为本地检索、`tools: []` 名不副实 |

格式样例：`bench/distill/cases/tabular/tab-5001/`（完整走过全部闸门）、`bench/distill/cases/hybrid/hyb-5006/`（两轮反问）、`bench/distill/cases/notool/nt-5001/`（闲聊）。

**覆盖 `drafting-brief.md` 的地方**：

| brief 原文 | 蒸馏题改为 |
|---|---|
| 写到 `bench/workbank/cases/<scenario>/<id>/` | 写到 `bench/distill/cases/<scenario>/<id>/` |
| canary `WORKBANK-CANARY-<hex>` | `DISTILL-CANARY-<hex>`，写 `WORKBANK-CANARY` 会被 lint 打回 |
| 4 题一族（L0→L1→L1→L2） | 每族 ≤ 3 题；难度配比 L0 35% / L1 45% / L2 20% |
| `author: llm:glm-drafter` | `author: llm:glm-5.3-flash-b04` |
| 每题最后一轮都追加 UNKNOWN 答案契约 | smalltalk 与拒绝题（beyond_capability / TR-NOCAP）**不加**，判据写法见 `distill-workflow.md` §2.5 的 expect 表和 §4.3、§4.3.1 |
| 自检命令在 `bench/workbank/` 下跑 | 在仓库根目录跑 §3.3 的命令 |
| 可以参考 `bench/workbank/cases/` | **不得读** `bench/workbank/cases/`、`cases-shelved/`、`reports/`、`ledger/`（`distill-workflow.md` §2.1） |

### 3.2 b04 额外规定

| 项 | 规定 |
|---|---|
| ID | 每个场景从 `<abbrev>-6001` 起连续编号 |
| `tags.author` | `llm:glm-5.3-flash-b04` |
| canary | `DISTILL-CANARY-<8位hex>`，每题不同 |
| family | 前缀 `fam-<abbrev>-b04-`，每族 ≤ 3 题（TR-ABSENT 成对为 2） |
| stable_fact | 本批不出 |
| 反问题判据 | 除了 `output_contains_any` 的问句词表，还要用 `output_contains` 要求出现候选项名字 |
| 数值题题面 | 答案契约前加 `Give the number alone, as digits, with no label.` |
| 追问型第 2 轮 | 不重复第 1 轮背景，只写追问 + 答案契约 |
| 自己出的题 | 不得用 step.py 解 |

### 3.3 交付前自检（全部通过）


```bash
bin/rwkv-lab bank lint --fix --canary-prefix DISTILL-CANARY --cases bench/distill/cases
bin/rwkv-lab bank lint --canary-prefix DISTILL-CANARY --case <dir>
bin/rwkv-lab bank verify --cases bench/distill/cases/<scenario>
bin/rwkv-lab corpus loadcheck --cases bench/distill/cases
```

## 4. 子 Agent 简报

**解题**（每次领 10–15 题）：

```
你为 RWKV-Agent 生产训练轨迹：扮演本地 Agent 模型，在真实 harness 里逐步做题。
必读并照做：docs/distill/distill-b04-glm.md §2。
本次题目（按顺序做）：
  <case_dir 1>
  <case_dir 2>
  …
本组题型：<task_type>。<W0 写：全部零调用，第 1 步直接作答；beyond_capability 可以先查工作区再拒绝>
不要跑 git，不要改任何文件，不要跑 collect.py。
交付：每题的 case_id、PASS/FAIL、步数。
```

**出题**：用 `distill-workflow.md` §2.7 的模板，并追加：

```
本批是 b04：本次 ID 从 <abbrev>-<起始号> 起；tags.author 用 llm:glm-5.3-flash-b04；family 前缀 fam-<abbrev>-b04-。
必读：docs/distill/distill-b04-glm.md §3.1 列出的全部材料，冲突时以 §3.1「覆盖」表和 §3.2 为准。不要用 step.py 解你自己出的题。
```

## 5. 主控命令

所有命令在仓库根目录执行。

**开工：**

```bash
git switch -c distill/b04
go build -o bin/rwkv-cli ./cmd/rwkv-cli && go build -o bin/rwkv-lab ./cmd/rwkv-lab
go test ./internal/lab/... ./internal/agent/eval/
mkdir -p runs/distill/b04/solve
printf 'case_id\tverdict\tnote\n' > runs/distill/b04/triage.tsv
grep -v '^#' bench/distill/tools/w0-cases.tsv | cut -f2 | split -l 13 - runs/distill/b04/w0-part-   # W0 分成 9 份
```

开工后**不得再重编 `bin/rwkv-cli`**，否则前后数据的 `wire_hash` 不一致。

**新题闸门**（每收到一份出题交付就跑；主控自己跑，不信子 Agent 的自检）：

```bash
bin/rwkv-lab bank lint --canary-prefix DISTILL-CANARY --cases bench/distill/cases
bin/rwkv-lab bank verify --cases bench/distill/cases
bin/rwkv-lab corpus loadcheck --cases bench/distill/cases
bin/rwkv-lab bank dedup --cases bench/distill/cases
bin/rwkv-lab corpus decontam --test bench/workbank/cases --candidates bench/distill/cases --report runs/distill/b04/decontam-cases.jsonl
bin/rwkv-lab corpus decontam --test bench/workbank/cases-shelved --candidates bench/distill/cases --report runs/distill/b04/decontam-shelved.jsonl
```

不过闸门的题能快速改好就改，否则整题删掉，在 triage 里记一行 `<id>\tDROPPED\t<原因>`。不放宽判据，不调 decontam 阈值。

**存档**（每完成一份派单就做一次）：

```bash
python3 bench/distill/tools/collect.py
git add bench/distill/cases bench/distill/scripts/b04.jsonl bench/distill/tools docs/distill/distill-b04-glm.md
git commit -m "wip(distill): b04 存档"
```

`collect.py` 打印 `REJECT … tool call on zero-call turn` 时，说明该解题子 Agent 在零调用题上用了工具：把它剩下的题收回，换一个会话重派，并在简报里强调 §2 规则 1。

**收尾**（全部做完，或用户叫停时）：

```bash
python3 bench/distill/tools/collect.py
bin/rwkv-lab corpus render --cases bench/distill/cases --script bench/distill/scripts/b04.jsonl \
  --source distill-b04 --out runs/distill/b04/corpus
python3 -c "import json;print({json.loads(l)['meta']['wire_hash'] for l in open('runs/distill/b04/corpus/rows.jsonl')})"
bin/rwkv-lab corpus pack --rows runs/distill/b04/corpus/rows.jsonl --exclude bench/distill/exclude.jsonl --dry-run
tar czf outputs/distill-b04-solve.tar.gz runs/distill/b04
```

验收：`wire_hash` 只有一个值；`pack --dry-run` 退出码 0；render 的拒绝逐条写明原因。
写报告 `bench/distill/reports/b04.md`：各波次派出 / PASS / FAIL / collect 拒收 / 闸门删题数，triage 全文，kind 分布，零调用行占比，git commit。
最后提交：`git commit -m "feat(distill): b04 GLM 批次——<N> 条路径"`。不 push。

## 6. 不得做的事

- 解题者读 `case.json` / `NOTES.md`；出题者解自己的题。
- FAIL 后 `undo` 换答案重试，或删 `solve/*.json` 绕过。
- 手改 `solve/*.json`、`b04.jsonl`；剔除只走 `bench/distill/exclude.jsonl`。
- 为保题数放宽 `expect`、调阈值。
- 把 `runs/` 提交进 git。

## 7. 这些是正常现象

- step.py 每一步都从头重放整道题（不调模型，很快）。
- harness 判 PASS 但 collect 拒收：零调用纪律只在 collect 里检查。
- W0 的部分旧题 FAIL：已知部分旧题判据有问题，记进 triage，不修。
- hybrid 的反问题第 1 轮先查了工作区：允许；notool 的不允许。
- 训练行的终答后面没有终止符：已知问题，以后改 renderer 后对 `b04.jsonl` 重新 render。
