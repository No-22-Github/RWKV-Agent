---
name: rwkv-data-qc
description: RWKV-Agent 训练数据的品控、清洗、审阅流程——蒸馏轨迹（Agent 数据块）和日常对话块在出包前、加新批次后、或怀疑数据有问题时使用。用户说"洗数据""审一下数据""品控""查脏数据""数据质量""这批能不能用""reviewed 标记""清洗"，或要按 8:2 等配比算还缺多少数据时，一定要用。只是出新题（出题任务书）、跑老师、跑分时不用。
---

# rwkv-data-qc：数据清洗与审阅

第一次完整跑是 2026-11-03 的 v3.1 洗数据（汇总见 `bench/distill/v3.1/wash-summary-20261103.md`，标准见 `bench/distill/v3.1/wash-rubric.md`）。工具都在 `bench/distill/tools/think_sft/`（bench 是独立 git 仓库）。

## 0. 已拍板的口径（改口径就改这里，写日期）

| 口径 | 定于 |
|---|---|
| 思考和终答的语言跟**最近一条真实用户消息**走；工具结果、文件是什么语言不影响；路径、代码、字段名照原文 | 10-30 / 11-03 |
| 反问：信息不全时最多调一次 list_files，然后直接问，不能翻遍文件再问 | 11-03 |
| 多用 calculator 是好事，单个运算的小算式也不算脏 | 11-03 |
| 网页 fixture 不用 `.example`；存量由 wash_apply.py 统一换成正常后缀 | 10-21 / 11-03 |
| 不能有空转、复读、点破模拟环境（"示例 URL""虚构""测试数据"） | 10-21 |
| 不筛老师自称 Qwen/DeepSeek；终答 Markdown 是加分；终答不准裸 UNKNOWN | 10-14 前 |
| 要删步骤才能修好的轨迹（结构性问题）一律整条删，不做局部拼接 | 11-03 |
| 日常对话的思考靠规则删句修不干净（会误删英文歌名、弄乱缩进），整条删或让老师重写 | 11-03 |
| 配比按**计 loss 字符**算，目标日常对话 : Agent = 8 : 2 | 11-03 |

## 1. 先看台账，只审没审过的

```bash
python3 bench/distill/tools/think_sft/qc_ledger.py status --blocks <数据块目录>
```

台账 `bench/distill/qc/ledger.jsonl` 每行记一次审阅：哪条对话、内容指纹、标准版本、谁审、哪天、读得深浅（full=逐步读完 / skim=只扫过）、结论。对话被改过或重新渲染，指纹对不上，自动变成 stale（需重审）。**只审 never 和 stale**，已审的不重复读。

## 2. 扫描：规则 + 人工

按 `wash-rubric.md` 的标签表打标签（以对话为单位，即 `meta.case_id`），处理只分三种：drop / fix / keep。

**规则可以直接定案的**（实测误报约 0）：思考语言不符（`wash_rethink.py scan`）；反问前的工具次数；沙箱里调 bc/python/curl/apt-get；没写文件却说"已暂存"；同一文件两次 replace_lines；中文思考里的"草稿："标记；调目录外工具；收尾阶段吐调用、一步多调用、坏 JSON。

**只能当线索、必须人工读的**（误报率 86%–100%）：终答太短（"只回答数字"的题本来就短）；终答数字不在工具结果里（多是正常心算的合计）；空转和重复读（多是故意构造的被拒重试、写后回读）；`awk -F','` 切 CSV；点破环境的宽关键词（`.example`、"老师"、"测试"）；日常对话的复读、截断、语言错配。

**规则抓不到、只能读的**：方法不对但蒙对的答案；终答和工具结果或思考矛盾（星期、均值算错）；被强制收尾后说"没查到"其实没查；该反问却直接作答；两轮终答相同；日常数学题本身出错。

量大时按块分 4 个分片派 Sonnet 子 Agent 并行。坑：
- 子 Agent **不能写报告 .md**，要求它把报告放在回复里，由主 Agent 落盘。
- 子 Agent 改写思考可能被安全分类器拦下，不要换别的执行者绕过。思考语言统一走第 3 步的老师重写，不交给子 Agent 手写；这样也保住老师的思考风格。
- 每个分片交：`labels.jsonl`、`edits.jsonl`、`reviewed.jsonl`（只列真正读过的，标 full/skim）和扫描脚本。
- 历史里的空思考块、故意构造的"重复调用被拒"、计 loss 步之外的坏命令，都不算脏。

## 3. 修

修改清单只有两种操作（格式见 `wash_apply.py` 文件头）：整条 `drop`，或 `replace` 原文→新文。原文必须用脚本从行里截，不手打。

```bash
# 思考语言：千问重写（付费 API，先过用户）
source ~/.commandcode_key.sh
python3 bench/distill/tools/think_sft/wash_rethink.py scan --blocks <块目录> --out steps.jsonl
python3 bench/distill/tools/think_sft/wash_rethink.py rewrite --steps steps.jsonl --out rethink-edits.jsonl --limit 5   # 先试 5 步人工看
python3 bench/distill/tools/think_sft/wash_rethink.py rewrite --steps steps.jsonl --out rethink-edits.jsonl            # 可续跑

# 合并清单 → 自检 → 出新块目录（不覆盖旧目录）
python3 bench/distill/tools/think_sft/wash_apply.py --blocks <旧块目录> --edits all-edits.jsonl --check
python3 bench/distill/tools/think_sft/wash_apply.py --blocks <旧块目录> --edits all-edits.jsonl --out <新块目录>
```

- 同一步不要既交给千问又让子 Agent 改，冲突会报 "old not found"。用户中途换语言的对话，千问只改思考、终答语言还是旧的，整条删。
- 改完要重算 token（`rwkv-lab tokcount --jsonl`，它写 `text_tok`，改名成 `tokens`）、重建 `index.json`（字段同 `split_blocks.py`）。
- 验收：`pack.py --blocks <新块目录> --recipe <配比> --out <临时目录>`，再对 train/validation 跑 `rwkv-lab corpus segcheck`，必须 0 不一致；再用 `wash_rethink.py scan` 和 grep `.example` 查残留。

## 4. 记台账

```bash
python3 bench/distill/tools/think_sft/qc_ledger.py add --blocks <新块目录> --reviewed <分片>/reviewed.jsonl \
  --labels <分片>/labels.jsonl --rubric wash-v1 --by sonnet-wash-A --at YYYY-MM-DD
```

指纹按修改**之后**的内容算。被老师重写过、但没人读过新内容的对话，不要记成已审（先从 reviewed 名单里去掉）。

## 5. 统计与配比

洗完后按块算计 loss 字符（`index.json` 的 `trained_chars`）。8 : 2 的缺口 = 日常 / 4 − Agent；除以每条 Agent 轨迹的平均计 loss 字符（v3.1 约 1,040），就是还要补的新轨迹条数。只数条数会偏：日常每条的计 loss 字符是 Agent 的约 3.5 倍。

汇总写到 `bench/distill/<版本>/wash-summary-YYYYMMDD.md`：每块删/修/留、洗后剩余、规则误报率、缺的示范类型（统计题算完核对、写后回读、可疑就换办法、反问），作为下一批出题的依据。
