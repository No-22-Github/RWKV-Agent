# workbank —— 在 RWKV-Agent 现有 eval 里建手写题库（交接文档）

> 给本地编码 Agent。**加粗「不得」** 是硬约束，附理由。
> 配套两份参考资料：`authoring-guide.md`（出题手册）、`defect-archive.md`（模型缺陷档案骨架）。三份一起放进 `bench/workbank/docs/`。
> 本文件取代之前的 `work-bank-v0-handoff.md`（那份是模板代码生成路线，已废弃）。

## 0. 目标

在 RWKV-Agent 现有 `agent-eval --cases` 管线上，积累一套 **300 题左右的 work 侧 agent 题库**，配套逐次跑分账本和模型横测表，用来区分模型 / state / wire 的改进。题目由 LLM 起草、自动校验、人工审核后冻结。题库攒成、证明可比性后再拆独立项目，现阶段不做协议解耦，但**题目本身必须协议无关**（见 §2.3），为以后零迁移留路。

## 1. 边界

### 1.1 做什么

| 产出 | 位置 |
|---|---|
| 题目（每题一个目录） | `bench/workbank/cases/<scenario>/<id>/` |
| 出题手册 / 缺陷档案 / tag 词表 | `bench/workbank/docs/` |
| 校验与统计脚本 | `bench/workbank/tools/` |
| 跑分账本与报告 | `bench/workbank/ledger/`、`bench/workbank/reports/` |
| harness 小改 | `internal/agent/eval`、`cmd/rwkv-cli`（§4，四项） |

Python 脚本用 uv 在 `bench/workbank/` 下建 venv，不用系统 Python。

### 1.2 不做什么

- **不写题目生成器 / 变体生成代码。** 陷阱之间不正交（千分位叠合计行，合计行本身也得带千分位、题面也要改），生成器会退化成逐题代码。变体一律手写（LLM 起草），用 `family` tag 关联。
- **不导入、不派生 primitive-bench 的题。** 只参考它的设计模式。
- **不按已知 RWKV 缺陷定向出题**（预留 10% 名额，等缺陷档案里有「确认」级条目再补探针题）。第一批要宽，否则题库被当前模型绑架，横测对其他模型不公平，也发现不了新缺陷。
- **不做 LLM judge 判分。** 摘要类需求改成「写进指定格式的文件」再确定性判分。
- **不接真网络跑评测。** web 题走 per-case fixture。
- **不给模型代码执行工具。** 执行工具（bash/python 沙箱）另行立项；本阶段脚本类题由判分器离线运行模型写出的脚本。
- **不调 harness 救援参数、不改 wire 去刷题库分数。** 题库回答的是「谁更好」，不是「怎么调到好看」。

## 2. 题目

### 2.1 目录与文件

```
cases/tabular/tab-0007/
  case.json      # schema v5，单题（build 时合并）
  verify.py      # 从 fixture 独立算出期望答案 / 期望文件，打印 JSON
  NOTES.md       # 出题说明：每个陷阱埋在哪、为什么答案是这个、参考解步骤
```

ID：`<scenario 缩写>-<4 位序号>`，分配后不复用。

### 2.2 完整样例

`case.json`（L2：TR-SIGN + TR-NUMFMT）：

```json
{
  "id": "tab-0007",
  "description": "Net August revenue; refunds stored as positive amounts; amounts formatted with currency and thousands separators. WORKBANK-CANARY-3f9a1c2e",
  "category": "tabular",
  "tags": {
    "scenario": "tabular",
    "task_type": "reconcile",
    "traps": ["TR-SIGN", "TR-NUMFMT"],
    "trap_decoys": {"TR-SIGN": "15076.55", "TR-NUMFMT": "UNKNOWN"},
    "axes": ["OBS"],
    "level": "L2",
    "family": "fam-tab-reconcile-01",
    "ref_calls": 3,
    "fixture_bytes": 1840,
    "status": "draft",
    "version": 1,
    "author": "llm:<model-id>",
    "reviewer": null
  },
  "files": {
    "orders.csv": "order_id,date,amount\nA-1041,2026-08-02,\"$1,129.90\"\n...",
    "refunds.csv": "refund_id,order_id,amount\nR-77,A-1041,\"$129.90\"\n...",
    "README.md": "refunds.csv lists refunded amounts for orders in orders.csv.\n"
  },
  "web_fixture": [],
  "turns": [{
    "prompt": "What was our net revenue for August 2026 after refunds? Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.",
    "expect": {"expected_number": 14817.35, "tolerance": 0.01}
  }]
}
```

`verify.py` 约定：只用标准库；读同目录 `case.json` 的 `files`；打印 `{"expected_number": ...}` 或 `{"files": {...}}`；`tools/verify_all.py` 比对它与 `expect` 是否一致。

### 2.3 题目硬规则

1. **prompt 不得出现工具名**（12 个工具名，lint 检查）。理由：题目协议无关的前提；且点名工具会把 DEC/STP 轴变成指令遵循。
2. **需要答案的题，prompt 末尾追加逐字节相同的全局答案契约**：
   `Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.`
   只写文件的题改为追加 `When finished, reply DONE.`。理由：现有 `expected_number` 要求整段输出是纯数字；统一契约让格式成为全题共享的恒定要求，UNKNOWN 出口对所有题都开，不会成为缺数据题的提示。
3. **判分以结果为主**：答案 / 文件状态 / 离线脚本结果。过程约束只用 `forbidden_tools` 与 `max_calls`，**不得用 `required_tools` / `required_calls` 卡解题路径**——模型用 data_query 算对和读文件算对都该过。
4. **题面讲目标和语义，规则放 fixture，不得在题面暗示陷阱**（每个陷阱在手册里列了题面禁词，lint 检查）。
5. `description` 末尾带 canary `WORKBANK-CANARY-<8位hex>`；语料管线据此排除，**题目不得进训练语料**。
6. 首批只出英文题；中文镜像以后单独成套、单独报分。

### 2.4 固定工具目录（所有题相同）

`list_files` `read_file` `search_text` · `read_lines` `write_file` `replace_lines` `append_file` · `calculator` `data_query` `datetime`（固定时钟 `2026-09-16T10:00:00+08:00`）· `web_search`（Brave 形态）`web_fetch`（Tavily Extract 形态）

**不得按题增减工具**：目录影响「调不调」的决策。无 web 的题也注册 web 工具，fixture 为空时搜索返回空列表、fetch 返回固定 not-found 页。

### 2.5 web fixture

- 条目字段沿用 `WebFixtureEntry`，新增 `published_at`。
- 内容从 `web/recordings/` 的真实 Brave / Tavily 响应改写（换关键值、调日期），**不手写整条结果**。
- 每个 web 题在 `NOTES.md` 里列 5 个合理改写查询；`tools/web_hitcheck.py` 验证全部命中目标条目。
- 页面默认低于 fetch 压缩阈值；只有带 `TR-LONG` 的 web 题故意超过。

### 2.6 离线脚本判分（`expect.run`）

在最终 workspace 的副本上执行；`python3 -I -S`（隔离 site-packages）；超时 10s；无网络；stdout 逐行比较（只去行尾 `\r`）。可带 `hidden_files`，在另一组输入上运行，防止模型硬编码结果。

## 3. 出题流水线（LLM 起草 → 自动闸门 → 人审 → 冻结）

| 步 | 做什么 | 工具 | 通过条件 |
|---|---|---|---|
| 1 选槽 | 按配额表找空缺格子（scenario × level × trap） | `coverage.py --gaps` | — |
| 2 起草 | 把 `authoring-guide.md` + 槽位说明喂给 API 模型，产出 case.json / verify.py / NOTES.md | 你的并发 API | — |
| 3 lint | tag 合法、工具名 0 命中、题面禁词 0 命中、答案契约逐字节一致、`level` 与陷阱数/`ref_calls` 规则一致、fixture 大小与 LNG 一致、每个陷阱都有 `trap_decoys` 且不等于正确答案 | `lint.py` | 全过 |
| 4 verify | 运行 verify.py，与 expect 一致；对答案做一次破坏（数值 +1 / 删一行），判分器必须判失败 | `verify_all.py` | 全过 |
| 5 查重 | 同 scenario 下题面 3-gram Jaccard > 0.6 或 fixture 数值集合高度重合 → 标记 | `dedup.py` | 无标记或人工确认 |
| 6 求解检查 | 用一个强 API 模型经 `agent-eval` 跑 draft 题 k=2 | `agent-eval --include-draft` | 失败的题进人审优先队列（**不自动淘汰**，可能是真难题） |
| 7 人审 | 看 NOTES.md 与强模型轨迹：答案唯一？陷阱真的埋上了？有无夹带提示？ | 人 | `status: reviewed` |
| 8 冻结 | 批次跑完无返修 → `frozen` | 人 | — |

**Agent 不得自行把 status 改成 reviewed / frozen。** 冻结后改题必须 `version+1`，并写入 `docs/changelog.md`（原因：修 bug / 改标 / 返修），账本里旧版本的 run 自动标为不可比。

起草时容易出的问题（写进起草 prompt，也作为人审清单）：
1. **verify.py 与 expect 出自同一次生成，错得一致。** 所以第 6 步强模型求解是必须的第二来源；二者不一致一律人审。
2. **在题面或 README 里「好心」解释陷阱**（"note: the last row is a total"）。这正是 fork 版 primitive-bench 被改废的路径。
3. **陷阱叠太多**，L1 写成了 L3。以 tag 计数规则为准，不按「感觉」。
4. **fixture 一看就是造的**：`foo`/`example`/整数金额/连续编号/所有题同一批人名。手册里有表面多样性要求。
5. **答案有两种合理解读**。人审时问：换一个认真的人来做，会不会得出另一个答案？

## 4. harness 改动（只做这四项）

**H1 case schema v5**（v4 照常加载）
- `tags`：对象，原样进 run.json / summary / trace
- case 级 `web_fixture`（含 `published_at`，透传到 `WebSearchResult.PublishedAt`）。**不得继续用全局 `--web-fixture` 跑题库**：几百题共用一份子串匹配的 fixture 必然串题。
- `expect.files`：`{path: {equals | contains[] | absent | unchanged}}`，`unchanged` 与初始 fixture 逐字节比
- `expect.run`：见 §2.6
- `expect.max_calls`：`{tool: n}`，**按模型发出的调用计数，含被 duplicate 拒绝的**——否则 harness 判重把循环藏起来
- 放宽「每轮必须声明工具期望」：有 `expected_number / output_* / files / run` 任一即可
- 单题文件：`--cases` 接受目录，递归加载 `case.json`；`--include-draft` 控制是否加载 `status: draft`

**H2 `--tool-catalog work-v1`**：注册 §2.4 目录（固定时钟、强制 web 工具），manifest 记录目录 hash。

**H3 题级干预计数**：rescue / forced answer / duplicate reject 次数落到每题 trace，供账本区分「靠救援通过」。

**H4 seed 核实**：确认 `--seed` 是否被 rwkv_lightning 遵守，结果写进 manifest；不改后端。

负向单测必须有：`unchanged` 改一个字节必须失败；`max_calls` 在 duplicate 被拒的 trace 上必须计入；`run` 下 `import pandas` 必须失败；v4 旧 case 文件（boundary、smoke）跑分结果不变。

## 5. 账本、横测表、诊断

### 5.1 `ledger/runs.jsonl`（只追加，每次 run 一行）

`run_id` · `date` · `model_id` · `model_fingerprint` · `state_sha256`（无则 null）· `wire_profile` · `wire_hash` · `harness_version` · `scorer_version` · `bank_version`（合并后 cases 的 sha256）· `tool_catalog_hash` · `sampling` · `k` · `endpoint` · 汇总：`pass_mean` / `pass_all_k` / 按 level / 按 scenario / 按 trap / `protocol_invalid_rate` / `loop_rate`（触顶轮次或 duplicate reject ≥ 2 的题占比）/ `rescue_assisted_passes`

### 5.2 `ledger/cases.jsonl`（每 run × 题 × k 一行）

`run_id` · `case_id` · `case_version` · `k_index` · `passed` · `failures` · `tool_calls` · `ref_calls` · `redundancy`（tool_calls / ref_calls）· `max_turns_hit` · `duplicate_rejects` · `rescues` · `trap_hit`（答案等于 `trap_decoys` 中某值时填陷阱 ID，自动计算）· `trace_ref`

### 5.3 `ledger/labels.jsonl`（失败模式标注）

`run_id` · `case_id` · `k_index` · `mode`（必须在 `defect-archive.md` 词表内）· `note` · `labeler`（`human` / `llm:<id>`）· `confirmed`（LLM 预标需人确认后为 true）

### 5.4 可比性与报告

- **可比键** = (`bank_version`, `harness_version`, `scorer_version`, `tool_catalog_hash`)。只有可比键相同的 run 进同一张横测表。
- `reports/matrix-<bank_version>.md`：行 = 模型 × state × wire；列 = 总分（95% CI）、L0–L3、代价最高的 3 个 trap、loop_rate、protocol_invalid_rate、rescue_assisted。报分**按实测难度分段**，声明难度只用于配额。
- `tools/compare.py A B`：翻转清单（通过↔失败，附 trace 路径）+ 差值 bootstrap CI。**按 family 重采样**（无 family 的题各自成组）——同 family 变体高度相关，按题重采样会把 CI 算窄。可从 `scripts/bfcl-compare-runs.py` 改起。
- `tools/calibrate.py`：输出「声明难度 vs 实测通过率」偏离表（标 L1 但所有配置 < 20%，或标 L3 但所有配置 > 80%），供人工改标或返修。

### 5.5 每轮跑分后

1. 自动信号入账（5.1/5.2）
2. 按 level × scenario 分层抽 30–50 条失败轨迹，LLM 预标 → 人确认 → `labels.jsonl`
3. 更新 `defect-archive.md` 计数与状态（门槛见该文档）
4. 偏离表送人审；变更写 changelog

## 6. 配额

总目标 300（其中 30 题预留给缺陷探针，暂不出）。首批 270 按下表：

| scenario | 缩写 | 题数 | | level | 占比 |
|---|---|---|---|---|---|
| tabular 表格数据 | tab | 40 | | L0 | 15% |
| logs 日志与事件 | log | 32 | | L1 | 40% |
| config 配置 | cfg | 26 | | L2 | 30% |
| docs 文本文档 | doc | 22 | | L3 | 15% |
| filesystem 文件系统 | fs | 22 | | | |
| script 脚本（离线判分） | scr | 32 | | | |
| code 代码只读与小修 | code | 22 | | | |
| web 网络搜索 | web | 30 | | | |
| hybrid 搜索+本地 | hyb | 22 | | | |
| notool 不该用工具 | nt | 22 | | | |

每个 scenario 内 level 比例同右表，允许 ±1 题偏差。`coverage.py` 从 tag 实时统计并输出空缺。

## 7. 里程碑

**M0 核实（0.5 天，阻塞）**，结论写 `docs/M0-findings.md`：
- `data_query` 是否自动解析 `$1,234.50`、`NA`（若是，`TR-NUMFMT` / `TR-MISSING` 在手册里要改埋法）
- `list_files` 是否列隐藏文件、`truncated` 是否对模型可见
- fetch 压缩阈值的实际 token 数
- seed 行为（H4）；现行 wire 的准确 profile 名

**M1 harness（2 天）**
```bash
go test ./internal/agent/eval/... -run 'SchemaV5|WorkCatalog|MaxCalls|RunCheck|DirCases'
```
验收：§4 负向单测存在且通过；boundary/smoke 结果不变。

**M2 工具与文档（1–2 天）**：`docs/tag-vocab.json`（从手册抽出的机器可读枚举）、`lint.py` `verify_all.py` `dedup.py` `web_hitcheck.py` `coverage.py` `build.py` `ledger.py` `compare.py` `calibrate.py`。
验收：故意在一题 prompt 里写 `read_file`，lint 必须失败；故意改 expect +1，verify_all 必须失败。

**M3 试点 40 题（闸门）**：10 个 scenario 各 4 题（L0/L1/L1/L2），走完 §3 全流程；跑 G1K（现行 wire，无 state）与 Qwen3-8B INT8，各 k=4，入账，做第一轮标注。
```bash
uv run tools/build.py --status reviewed --out out/workbank.json
rwkv-cli agent-eval --cases bench/workbank/cases --tool-catalog work-v1 --file-tools lines \
  --profile <M0 确认> --temperature 0.3 --case-parallelism 256 \
  --output runs/workbank/<config>-k<i>
uv run tools/ledger.py ingest runs/workbank/<config>-k*
```
闸门：两个配置各自 4 次总分极差 ≤ 5pp；两个配置上都满足 L0 ≥ L1 ≥ L2 的平均通过率；强模型求解检查里无法解释的失败 ≤ 10%。不过闸先修手册与流水线，不扩量。

**M4 分批扩到 270**：每批约 50 题，走 §3；每批跑完做 §5.5。攒到 270 且连续两批无大规模返修，出第一份 `reports/matrix-<bank_version>.md`，再评估拆独立项目。
