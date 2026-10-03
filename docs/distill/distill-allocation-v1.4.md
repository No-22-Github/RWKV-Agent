# 蒸馏数据构成规划 v1.4 —— 实施规格书

> 给执行 Agent：读完能直接开工出题、蒸馏、渲染、打包。文中「必须 / 不得」是硬约束，每条附理由。
> **核心章节是 §3（新增题类与样例）和 §4（终答形态规则）**，其余章节是外壳。
> 配套：[distill-workflow.md](distill-workflow.md)（流水线 S0–S8 照旧）、[distill-allocation-v1.3.md](distill-allocation-v1.3.md)（v1.3 规则未被本文改写的继续有效）。

## 0. 目标

v1.3 state（v13b-s688）把 workbank 干净 112 从 4.0 提到 24.7（三次均值），但 bfcl-product 从 39.7 掉到 30.0（中文 29 → 21），
且引入了新失败「短垃圾终答」。v1.4 在**不动格式**的前提下补三件事：

1. **终答形态去偏**：纯值终答从 70% 降到 ≤40%，消除「写个短词就 `\n\nUser:`」。
2. **把 bfcl 拉回来**：遵守「不要调用工具」、只调本轮提供的工具、反问点名缺的参数。
3. **补 v1.3 归因出来的真不会**：写任务闭环、表格/日志的工具化处理、信源优先级、查不到时写清楚。

最关键的取舍：**去掉「只给答案」模板不等于让终答变长**。新终答是「一到两句、先给结论、再说依据」，不是报告。

## 1. 依据

| 来源 | 结论 | 文档 |
|---|---|---|
| v1.3 state 跑分 | workbank +21、bfcl −10（中文 −8）、两个 lr 无差别、workbank 到 3 epoch 仍在涨 | [state-v13-20261003/REPORT.md](../evaluations/state-v13-20261003/REPORT.md) |
| 答错逐题归因（62 题） | 收尾兜底 8、**短垃圾终答 15**、写任务 13、数据处理 14、信源/编造 8、心算 3、知识 1 | [WRONG-ANSWERS.md](../evaluations/state-v13-20261003/WRONG-ANSWERS.md) |
| bfcl 掉分（none 对、state 错 28 题） | 不听「不要调用工具」12、调用未提供的 `web_search` 6、收尾吐调用 9、反问没点名参数 | 同上 REPORT §5 |
| 格式消融 | g1k 仍最稳，Hermes 格式不可用；**v1.4 不换格式** | [g1k-official-format-20261003/REPORT.md](../evaluations/g1k-official-format-20261003/REPORT.md) |
| v1.3 训练集构成 | 纯值终答 70%（b05 存量 881/1130 行）；中文 23.9%；多轮 10.5%；`data_query` 3.8%；write+script 5.6%；工具清单最小也有 8 个 | [clean-v13.md](reports/clean-v13.md) |

bfcl-product 只提供 `list_files` / `read_file` / `search_text` / `no_tool` 四个工具，v1.3 训练集没有一行的清单少于 8 个——这是「调用未提供工具」的直接原因。

## 2. 总览

| 批 | 内容 | 产出行（估） | 老师 |
|---|---|---|---|
| b09 存量改造 | §3.1 M1：b05 纯值题删契约、只改写终答（不重做题）；§3.9 按 family 封顶 | 替换 ~450 行，删 ~150 行 | 改写模型（每行一次调用），不跑老师 |
| b10 新题 | §3.2–§3.8 M2–M8 | ~1000 行 | 按类，见各节 |
| b11 收尾恢复 | §3.10 N10 扩量（含写/脚本任务） | ~200 行 | 无（机械变换） |
| 合计 | v1.3 2051 − 150 + 1000 + 100（N10 净增） | **≈ 3000 行** | |

**不做什么**（点名，免得两套都做）：

- 不改 wire、System、工具 schema：`wire_hash` 必须仍是 `707c67403b1b…`，因为推理端与 state 都绑定这套字节；格式消融已证明换格式不提分。
- 不用 Hermes / think / 预填格式渲染语料。
- 不新增工具；「小清单」只靠题目级 `offered_tools` 过滤现有 work-v1。
- 不出裸 `UNKNOWN` 终答，也不再新增带「reply exactly UNKNOWN」契约的题（理由见 §4.2）。
- 不碰 `bench/workbank/cases`、`bench/holdout/p13`、bfcl-product 源码：它们是考卷。

## 3. 题类规格（核心章节）

通用规定（每类都适用，除非该节另写）：

- ID 从 **8001** 起按场景递增（v1.3 已用到 7775）；`family` 用 `fam-<abbrev>-b10-<slug>-NN`；description 以 ` DISTILL-CANARY-<8 hex>` 结尾。规则同 workflow §2.2。
- 每个种子工作区最多 5 条路径；新 family 不复用 base700 / workbank 的工作区与文件名。
- 去污染四面：`--test bench/workbank/cases`、`--test bench/holdout/p13`、`--test-suite bfcl-product`、`--test bench/distill/cases-shelved`，0 flagged 才进 S4。
- **不得**取材于 workbank、p13-holdout、bfcl-product 的考题：本文的归因来自对 workbank 的逐题阅读，但出题只能借「失败类型」，不能借场景、文件名、公司名、数值。本文样例都是新编的示意，照样例的**形态**出题，不要照抄样例本身（每个样例最多派生 1 个 family）。S3 decontam 命中即弃。
- 「中文」列是该类中文题的**下限**。中文题的工作区文件内容也用中文（表头、日志、文档），不是英文工作区配中文题面。
- 终答一律按 §4。

### 3.1 M1 终答形态去偏（b09，改写存量终答，~450 题，**不重做题**）

**治什么**：短垃圾终答（15 题）。训练终答 70% 是纯值、紧跟 `\n\nUser:`，模型学成「写个短东西就结束」。

**为什么改写而不重做**：b05 的工具轨迹已经验证能做对，只有终答形态有问题。只改最后一项输出：成本是每行一次 LLM 改写 + 一次重放（重做要老师 k=3 + S5 质检）；工具部分原样保留，不会带进新的轨迹变化；v1.4 的收益也能干净地归到「终答形态」这一个变量上。

**脚本格式**（`bench/distill/scripts/b05-baseline.jsonl`，一行一条路径）：

```json
{"case_id": "cfg-5001--p1", "outputs": [
  {"text": "<tool_call>{\"name\":\"list_files\",\"arguments\":{\"path\":\".\",\"max_depth\":4}}</tool_call>", "supervised": true},
  {"text": "<tool_call>{\"name\":\"read_file\",\"arguments\":{\"path\":\"config/production.yaml\"}}</tool_call>", "supervised": true},
  {"text": "576", "supervised": true}]}
```

M1 只改 `outputs` 的**最后一项** `text`，其余各项逐字节不动。

**步骤**（新工具 `bench/distill/tools/v14_rewrite_finals.py`，输入 b05 脚本 + 渲染行，输出 b09 脚本）：

1. **选题**：b05 里终答为纯值的路径（判定同 [clean-v13.md](reports/clean-v13.md) 的口径），按 family 均匀抽 **450 条**，每个 family 最多 3 条。只选单轮题（多轮题的终答改写会牵动后续轮次，不在本批）。
2. **改题面**：删掉题面里的答案契约句——`Reply with only the final answer.`、`If you cannot determine the answer, reply exactly UNKNOWN.`、`Just the number`、`只回数字` 等（正则沿用 v1.3 `v13_edit_contracts.py`，再加中文四种写法）。`tags.answer_style` 设为 `natural`，`tags.version` +1。
3. **改判据**：`output_equals` / `expected_number` → `output_contains`（值的规范写法）或保留 `expected_number` 并加 `"number_in_text": true`（**待 M0 确认 scorer 是否支持从句子里取数**）；另加 `"max_output_chars": 300` 与 `"output_contains_token": true`（值必须作为独立词元出现：子串匹配下 `5` 会命中 `2026-05`、`95` 会命中 `95000`，b09 实测 450 条里 19 条改错值仍能通过）。不得加「或者 UNKNOWN」之类兜底选项。
4. **改写终答**：对每条路径调用一次改写模型（GLM 或 DeepSeek，非思考模式，温度 0.7），输入 = 新题面 + 该路径全部工具调用与工具结果 + 原终答；要求见下方「改写提示要求」。
5. **机械校验**（任一条不过就丢掉这条，**不修**）：
   - 改写后的终答包含原值（数值按规范写法比较，允许千分位逗号差异）；
   - 终答里出现的文件路径，必须是这条轨迹里实际 `read_file` / `read_lines` / `data_query` 过的路径；
   - 终答里出现的数字，必须出现在原值、题面或某次工具结果里（防编造）；
   - 长度 ≤300 字符；不含 `<tool_call>`、`<tool_response>`、角色标签、`✿`；
   - 语言与题面一致。
6. **输出**：新脚本写成 `bench/distill/scripts/b09-m1.jsonl`，`case_id` 用新路径号 `--p90`（如 `cfg-5001--p90`），`supervised` 照抄。
7. **排除旧路径**：被改写的那道题，b05 里**所有**旧路径（不止被选中的那条）和 b08 里由它派生的收尾恢复路径（`--p81`）都写进 `exclude.jsonl`（batch 分别写 b05 / b08，reason「v1.4 M1 改写终答」）。判断「已排除」要按 (case_id, batch)：pack 只认本 batch 的条目。理由：存量行是从题目文件重新渲染的，题面改了以后，旧路径会套上没有契约的新题面重新渲染，且仍能通过 `output_contains`，正好造出「用户没要求只给值、模型却只回一个值」的最坏组合。
8. **重放**：`corpus render --script bench/distill/scripts/b09-m1.jsonl --source distill-b09`，按新判据判分，不过的路径照常进 rejects。
9. **抽检**：每 50 条人工看 3 条「依据讲得对不对」，结果贴进 b09 报告。重点看下方「改写救不了的情况」。

**改写提示要求**（写进 `v14_rewrite_finals.py` 的提示词，不得删减）：

- 一到两句：先给结论（含原值），再说依据（哪个文件 / 字段 / 哪条规则覆盖了哪条）。
- **句式要有变化**：提示里给 5 种不同开头和结构的示例（结论在前 / 依据在前 / 「按 X 算是 Y」/ 带单位换算说明 / 带对比项），并要求不要总用同一种。理由：全写成「X is Y (file)」会练出一个新的固定句式，和纯值一样僵化。
- 只能用轨迹里出现过的信息，不得补充轨迹之外的事实；不得改动原值。
- 不写「根据工具结果」「I used read_file」这类描述过程的话：说依据是哪份文件，不是说调了什么工具。

**改前改后样例**（示意，非真实题）：

| | 题面 | 终答 |
|---|---|---|
| 改前 | The kiln-monitor exporter is being moved to a new scrape pool; what scrape interval does it run with in staging? Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN. | `20` |
| 改后 | The kiln-monitor exporter is being moved to a new scrape pool; what scrape interval does it run with in staging? | `It scrapes every 20 seconds in staging: environments/staging.env overrides the 60-second default in config/exporter.yaml.` |

**改写救不了的情况**：原轨迹本身是「没查完、碰巧猜对」的路径（例如只读了默认配置，值恰好没被覆盖）。只回一个值时看不出来，改写成「依据是某文件」反而把错误推理写明白了。校验第 2 条只能保证引用的文件读过，保证不了推理对。抽检时专看这类；抽检里发现 ≥2 条，就对该 family 的全部改写行做逐条人工检查。

**保留比例**：b05 剩余纯值题不动。改完后全量纯值终答目标 ≤40%（§5）——仍有约 1/3 的题保留「只给答案」，因为真实用户也会这么要求，模型必须两种都会。

### 3.2 M2 查不到 / 目标不存在：写一段说明（b10，150 行，中文 ≥50%）

**治什么**：cfg-0012（目标 profile 不存在，拿诱饵作答）、hyb-0009 / hyb-0012（编造费率）、fs-0011 类。**用户硬要求：不能只回几个字，要写一段解释，否则又练僵化。**

**题型配比**：目标对象不存在但有相近诱饵 60、数据里确实缺这一项 40、需要的外部信息拿不到（网页 fixture 返回 `error`）30、只能回答一部分 20。

**终答必须包含三样**：查了哪些地方；要找的东西不在其中（点名）；用户可以怎么补 / 下一步。有相近信息时点明「只找到 X，它不是你要的 Y」。2–4 句，不编数值。

| ID 示例 | 题面 | 工作区要点 | 期望终答（老师输出须满足） | 判据 |
|---|---|---|---|---|
| cfg-8001 | 渡口票务系统要在 南湾码头 上线，帮我看看 南湾码头 的站点配置里还缺哪些平台要求的键。 | `站点/` 下只有 `北港码头.yaml`、`西渡码头.yaml`；`平台/必填键.yaml` 列出必填键 | 查了 站点/ 目录，只有北港码头和西渡码头两份配置，没有南湾码头，所以没法判断它缺哪些键；如果南湾码头的配置放在别处请告诉我路径，或者我可以按必填键清单帮你起一份。 | `output_contains_any: ["南湾"]` + `output_contains_any: ["没有","不存在","找不到"]` + `output_excludes`（北港 / 西渡配置里缺的键名，诱饵）+ `min_calls: 2` |
| hyb-8002 | Ops wants this quarter's berth-licence fee for our dredger fleet at the rate the Hollin Estuary Trust publishes. | `fleet/dredgers.csv` 在；web fixture 对 Trust 费率页返回 `error` | Gives the fleet figure it read from the CSV, says the Trust's rate page could not be fetched, so the fee is not computed, and asks for the published rate or another source. | `output_contains_any: ["could not","couldn't","unable"]` + `output_contains`（CSV 合计值）+ `output_excludes`（任何金额）+ 至少两次不同调用 |

**这不是 bug**：这些题的正确终答里没有题面要的那个数。不要为了让判据「更像普通题」而给它补一个答案。

### 3.3 M3 遵守「不要调用工具」/ 沿用上一轮证据（b10，180 行，中文 ≥70%）

**治什么**：bfcl 中文掉分最大头（12 题）：用户明确说不要调工具、或上一轮已有证据时，state 照调不误。

**题型**：

| 子类 | 行 | 结构 |
|---|---|---|
| 两轮复述 | 80 | 第 1 轮正常读文件；第 2 轮「不要调用工具，根据上一轮读到的内容回答 X」 |
| 单轮显式禁令 | 50 | 「不用查文件，直接告诉我 …」，问题本身靠常识可答 |
| 反问点名参数 | 50 | 缺路径 / 缺关键词 / 缺时间范围；「先问我，不要调用工具」；第 2 轮补参数后完成 |

| ID 示例 | 第 1 轮 | 第 2 轮 | 判据 |
|---|---|---|---|
| fs-8003 | 帮我看一下 采购/供应商名录.md 里登记的冷链供应商叫什么。 → 读文件，答「冷链供应商是 澜川冷运（采购/供应商名录.md）」 | 不要调用工具，根据刚才读到的内容，再说一遍冷链供应商是谁。 → 「刚才名录里登记的冷链供应商是 澜川冷运。」 | 第 2 轮 `tools: []`、`forbidden_tools: ["*"]`、`output_contains: ["澜川冷运"]` |
| nt-8004 | 我要你汇总上周的退货单，但还没告诉你文件放在哪。先问我，不要调用工具。 → 「退货单文件的路径是什么？比如在 售后/ 下的哪个文件。」 | 售后/退货-第38周.csv → 读并作答 | 第 1 轮 `tools: []` + `output_contains_any: ["路径","哪个文件","放在哪"]`；第 2 轮 `required_tools: ["read_file"]` + 值 |

**不得**照搬 bfcl-product 的题材：`facts/*.txt` 单行键值、`config/app.env` 的 TOKEN、`metrics/summary.txt` 的 score、`multi_turn_base_*` 的「重复这个值」句式都在考卷里，用了 decontam 会命中，没命中也等于背题。

**反问措辞**：必须点名缺的是哪个参数（路径、文件名、关键词、时间范围），不得只问「哪个文件或目录？」这种泛问。理由：bfcl 的缺参题判的就是「问对了缺什么」，泛问在真实使用里也让用户多答一轮。
**不得**为了命中判据把「路径」二字硬塞进每句话——判据用 `output_contains_any` 列 3–4 个等价说法。

### 3.4 M4 小工具清单：只调本轮提供的工具（b10，150 行，中文 ≥40%）

**治什么**：bfcl irrelevance 里调用未提供的 `web_search` / `calculator`（6 次）。v1.3 最小清单仍有 8 个工具，模型背熟了整套目录。

**清单**：用题目级 `offered_tools`（v1.3 §2.12 已实现，按名字过滤 work-v1；`no_tool` 由 abstain 自动附带，不写进列表）。

| 清单 | 行 | 题目内容 |
|---|---|---|
| `["list_files","read_file","search_text"]`（= bfcl-product 的清单） | 70 | 一半是工作区题（正常用这三个工具），一半是不需要工具的题：算术、常识、改写、翻译 |
| `["read_file","calculator"]` | 30 | 需要查网页的问题：没有网页工具 → 说明无法联网核实，给出能给的部分 |
| `["list_files","read_file","search_text","calculator","data_query"]` | 50 | 表格题，混进需要写文件的请求：没有写工具 → 给出结果并说明需要用户自己写入 |

| ID 示例 | offered_tools | 题面 | 期望行为 | 判据 |
|---|---|---|---|---|
| nt-8005 | list_files, read_file, search_text | 一批货 12 箱、每箱 36 件、损耗 3%，实际能入库多少件？ | 直接算：12×36=432，432×0.97=419.04，答约 419 件（不调用任何工具） | `tools: []` + `output_contains_any: ["419"]` |
| web-8006 | read_file, calculator | What is the latest stable release of the pellucid-cache client library? | 说明本轮没有联网工具，无法核实最新版本；如工作区有相关记录可读，没有就建议用户去官方发布页确认 | `tools: []` 或仅 `read_file` + `output_contains_any: ["cannot","can't","unable","no web"]` + `output_excludes` 编造版本号 |

**这不是 bug**：nt-8005 不调计算器是对的——清单里没有计算器。和 §3.8「有计算器就用」不矛盾：规则是「用清单里有的」。
scorer 已把调用未提供的工具判为失败（提交 70e604f），S5 会把这类路径筛掉，不需要额外判据。

### 3.5 M5 写任务闭环（b10，180 行，中文 ≥30%）

**治什么**：写任务 13 题：没写就回 DONE、写坏文件、把内容写进回复、`replace_lines` 行号用错、覆盖掉要求保留的注释。

**统一轨迹要求**（老师路径不满足就在 S5 丢弃）：先读目标文件 → 写（`write_file` / `replace_lines` / `append_file`）→ **回读一次校验** → 终答一句话说明改了哪个文件、哪一行或哪个值；题面要求「reply DONE」时，说明之后另起一行写 `DONE`。

| 子类 | 行 | 要点 |
|---|---|---|
| 局部替换保留注释 / 缩进 | 50 | 目标行带行尾注释（形如 `采样间隔秒: 30   # 2026-07 校准后调整`），替换只改值 |
| 多行替换的行号范围 | 30 | 要改的是连续 2–4 行，`start_line`/`end_line` 必须覆盖全部，`content` 行数与之相符 |
| 依据另一文件改值 | 40 | 版本号来自 lock 文件 / 网页 fixture / 变更单，必须先读依据再写 |
| 新建报告文件 | 30 | 题面给出头部与格式；内容必须写进文件，回复里只说已写到哪里 |
| 信息不足不写 | 30 | 变更单缺目标值 / 指向不存在的环境 → 不写，按 §3.2 说明缺什么 |

| ID 示例 | 题面 | 判据 |
|---|---|---|
| cfg-8007 | 照 工单/GD-0417.txt 把 称重站 的 采样间隔秒 改成工单里的值，配置/称重站.yaml 里的注释和缩进要原样保留。改完回复 DONE。 | `expect.files["配置/称重站.yaml"]` 精确匹配（含注释行）+ 轨迹里写后有 `read_file` 同一路径 + `output_contains: ["DONE"]` |
| scr-8008 | meter_rollup.py 现在漏统计 readings/ 子目录里的文件，修好它，让 `python3 meter_rollup.py` 覆盖全部 water-*.csv。 | `expect.run`（stdout 精确匹配）+ 写后回读 |

**这不是 bug**：写后回读那一次 `read_file` 在 harness 看来不是重复调用（文件已变，`MutatesWorkspace` 会放行），不要把它当冗余调用删掉——它是要教的行为。

### 3.6 M6 表格 / 日志：工具化处理（b10，180 行，中文 ≥30%）

**治什么**：数据处理错 14 题，几乎都是在 `read_file` 原文上心算筛选。训练集 `data_query` 只占调用 3.8%。

| 子类 | 行 | 工作区要点 | 要求的工具 |
|---|---|---|---|
| 混合日期格式 | 40 | 同一列混 `2026/03/02`、`07-03-2026`、`Mar 11, 2026`、`2026-03-05T08:00:00Z` | `data_query` 归一后过滤；终答说明按什么口径算 |
| 时区换算 | 30 | 日志 UTC、题问新加坡 / 北京时间；或两个源一 UTC 一 SGT | `search_text` 定位 + `datetime` 或手算并在终答写明换算 |
| 筛选 + 连接 | 50 | 花名册 × 工时、库存 × 单价，带阈值（≥20 件）、部门、月份条件 | `data_query`（不许整读后心算） |
| 单位混排 | 30 | `elapsed` 列混 `940ms` / `1.6s`；金额混 `¥` / `元` | `data_query` 或 `calculator`，终答写换算口径 |
| 定位行号 | 30 | 300–2000 行源码 / 日志，问某定义或某事件在哪一行 | `search_text`（结果带行号），不许 `read_file` 后数行 |

判据统一：值判据 + `required_tools` + 题目级 `expect.max_calls: {"read_file": 1}`。至少 1/4 题含「`data_query` 列名写错 → 看错误 → 改对重查」（沿用 v1.3 N11 要求）。

| ID 示例 | 题面 | 期望 |
|---|---|---|
| tab-8009 | 青梧家具 5 月 1 日到 10 日（含）一共发了多少单？发货流水在 物流/发货记录.csv。 | 具体数随工作区而定；终答说明日期列格式不统一、已归一后计数 |
| log-8010 | 灯塔监测服务升级到 beacon-svc-3.7.1 之后记录的第一条 ERROR 是什么时候？用北京时间 YYYY-MM-DD HH:MM:SS。 | 具体值随工作区而定；终答写明原始 UTC 时间与换算 |

### 3.7 M7 信源优先级（b10，80 行，中文 ≥30%）

**治什么**：web 题信博客 / 社区 wiki 而不信官方发布页（3 题，其中一题官方页已经抓到却仍答了博客的版本）。

**web fixture 结构**（每题都要有）：搜索结果里同时出现官方页（项目自己的域名、release notes / changelog）和二手页（博客、论坛、wiki），二者版本或日期**不一致**；官方页内容带日期。

| 子类 | 行 | 期望 |
|---|---|---|
| 官方 vs 二手冲突 | 40 | 以官方页为准；终答写明依据是官方发布页，必要时一句话点出二手页的说法过时 |
| 只抓到二手页 | 20 | 官方页 fixture 返回 `error`：给出二手页的说法并标明「未在官方页核实」（`must_state_unverified`） |
| 预览版 vs 正式版 | 20 | 官方页同时列 preview / rc 和 stable：题问「客户能拿到的」时答 stable |

判据：`output_contains`（官方值）+ `output_excludes`（二手页的值）+ `required_tools: ["web_fetch"]`。

### 3.8 M8 算术交给计算器（b10，60 行，中文 ≥50%）

**治什么**：心算换算错 3 题（2.5×3600 答成 90）。none 会调计算器，state 学成了零调用心算——v1.3 零调用题里有算术。

规则：**本轮清单里有 `calculator` 且答案需要计算**时，必须调用它；清单里没有时直接算并写出算式（见 §3.4）。
题型：单位换算、百分比、按天 / 按小时折算、多项求和。判据：`required_tools: ["calculator"]` + `expected_number`。
同时 S5 加一条过滤：v1.3 存量里「题面需要计算、清单有计算器、路径却零调用」的行，从训练集剔除（写进 `exclude.jsonl`，reason「v1.4 M8 心算」）。
**按难度区分**（`bench/distill/tools/v14_m1_closeout.py`）：终答数值不在上下文里（确是算出来的）才算心算；其中一步就能得到、且是 ≤100 的整数加减 / 一个因数 ≤12 另一个 ≤100 的乘法 / ≤1000 被 ≤12 整除的，属心算合理，保留；其余（小数、多步、带非整常数的换算）剔除。理由：两位数相加也去调计算器是多余的，且全剔会把零调用占比继续往下压。b09 实测剔除 143、保留 25。

### 3.9 存量封顶（b09，删 ~150 行）

v1.3 训练集 b05 占 55%（1130 行，几乎全英文、单轮、纯值），拖低中文与多轮占比。
按 `tags.family` 封顶：**每个 family 最多 3 行**（优先保留 M1 改写后的行和带 `--p81` 收尾恢复的行），超出的写进 `exclude.jsonl`（batch b05，reason「v1.4 family 封顶」）。
执行前先跑一遍统计并把「将删除的行数按 kind 分布」贴进 b09 报告；若删除超过 250 行，停下来报告，不要继续——说明封顶值需要调。

### 3.10 N10 收尾恢复扩量（b11，~200 行）

沿用 v1.3 `bench/distill/tools/v13_closeout.py` 的机械变换（不出新题），两处改动：

1. 来源换成 v1.4 最终通过的脚本（b09 + b10），路径编号 `--p91`（M1 改写用的是 `--p90`，不要撞号）。
2. **写任务和脚本任务也要覆盖**：v1.3 只从单轮读取题里取；归因里收尾失败的有一半是写 / 脚本任务。目标 200 行里 write+script ≥ 60 行。
   插入的重复调用仍只允许 `list_files` / `read_file` / `read_lines` / `search_text`（web 工具可重放，走不到收尾）。

**这不是 bug**：插入的重复调用在 loss 区间之外（`supervised:false`），训练时不学它；学的是被拒之后的文字终答。

## 4. 终答形态规则（所有新增行与改写行）

### 4.1 按情况选形态

| 情况 | 终答 | 例 |
|---|---|---|
| 题面明确要求只给值（「只回数字」「Reply with only the final answer」） | 只给值 | `20` |
| 普通查值 | 一句话：结论 + 依据（文件、字段或口径） | `staging 的采样间隔是 20 秒：environments/staging.env 覆盖了默认的 60 秒。` |
| 查不到 / 目标不存在 | 2–4 句：查了哪、缺什么、下一步（§3.2） | 见 §3.2 |
| 只能答一部分 | 先给确定的，再点名没能核实的 | `华东区 5 月退货 312 单可以确定；华南的数据文件缺 5 月 20 日以后的记录，那部分没算进去。` |
| 写 / 改文件完成 | 一句话说明改了哪个文件、哪项；题面要求 `DONE` 时另起一行写 `DONE` | `已把 配置/称重站.yaml 的 采样间隔秒 从 30 改成 15，注释保留。`↵`DONE` |
| 闲聊 | 1–3 句自然回应，不提工具目录 | |
| 需要反问 | 一句问句，点名缺的参数（§3.3） | `退货单文件的路径是什么？` |

### 4.2 禁止的形态

| 形态 | 理由 |
|---|---|
| 裸 `UNKNOWN` / 「不知道」 | 用户明确要求：查不到要写一段解释，否则练成固定短词；v1.2 已练出过裸 UNKNOWN |
| 不是题面要求的单值短答（`Toolbox`、`—` 这类就是它的失败形态） | v1.3 纯值终答 70% 诱发了短垃圾终答 |
| 写了「DONE」但没调写工具，或写后没回读 | 归因 C 类 13 题 |
| 把要写进文件的内容放在回复里 | doc-0011 类 |
| 超过 600 字符（N5 类自然语言总结除外，上限按题放宽到 1200） | 沿用 v1.3 §2.4；长终答会压低训练 token 里的有效监督密度 |
| 终答里出现 `<tool_call>`、`<tool_response>`、角色标签、`✿` | 泄漏类失败 |

### 4.3 「只给值」还保留多少

改完后纯值终答占比目标 ≤40%（v1.3 为 70%）。中文题与英文题各自都要满足：不允许靠中文题都是句子、英文题都是纯值来凑平均。

## 5. 目标构成（v1.4 ≈ 3000 行）

统计口径沿用 [clean-v13.md](reports/clean-v13.md)：按每行最后一条真实用户消息判语言；harness 回执（`<tool_response>`、`Use the Tool results above`、`The tool call failed:`、`The … arguments were rejected:`、重复拒绝、`Tool execution is complete`）不算用户消息。

| 指标 | v1.3 实际 | v1.4 目标 |
|---|---|---|
| 纯值终答 | 70.0% | ≤40%（中英文分别满足） |
| 裸 `UNKNOWN` 终答 | 0 | 0 |
| 带 UNKNOWN 契约的题 | 19.7% | ≤10%（M1 删契约后自然下降） |
| 中文行 | 23.9% | ≥30% |
| 多轮行（≥2 轮） | 10.5% | ≥15% |
| 工具清单 ≤5 个的行 | 0 | ~7%（M4 150 行 + 部分 M3） |
| `data_query` 占全部调用 | 3.8% | ≥10% |
| write + script 行 | 5.6% | ≥12% |
| 写任务中「写后回读」的比例 | 未统计 | ≥90%（新增行） |
| 收尾恢复行 | 96 | ~200，其中写 / 脚本 ≥60 |
| 零调用（第 1 轮） | 26.5% | 22–28%（不下降，防 bfcl 过调用） |
| 首动作 `list_files`（用工具的首轮行） | 62.7% | ≤40%；题面给路径时 ≤10% |
| 单行 token | max 6925 | 硬上限 8128；>4096 的行 ≤15% |

## 6. 流水线与命令

流程照 workflow S0–S8，新增与改动如下（`$O=local/runs/distill/v14`）。

```bash
# S2 静态闸门（每批）
local/bin/rwkv-lab bank lint --cases bench/distill/cases --canary-prefix DISTILL-CANARY
local/bin/rwkv-lab bank verify --cases bench/distill/cases --strict-shape
# S3 去污染四面：--test 每次只接一个目录，--test-suite 与 --test 二选一，所以分四次跑，每次 0 flagged 才继续
for t in bench/workbank/cases bench/holdout/p13 bench/distill/cases-shelved; do
  local/bin/rwkv-lab corpus decontam --cases bench/distill/cases --test $t
done
local/bin/rwkv-lab corpus decontam --cases bench/distill/cases --test-suite bfcl-product
# S6 渲染：目录轮换照旧 0.4；题目级 offered_tools 优先于轮换
local/bin/rwkv-lab corpus render --cases bench/distill/cases --script bench/distill/scripts/b10.jsonl \
  --source distill-b10 --rotate-catalog 0.4 --out $O/b10
# S8 打包 + 转掩码格式（v1.3 训练输入一节的做法）
python3 bench/distill/tools/build_v13_suffix.py --rows $O/b09/rows.jsonl --rows $O/b10/rows.jsonl ... --out $O/rows-suffixed.jsonl
python3 bench/distill/tools/split_v13.py --rows $O/rows-suffixed.jsonl --train $O/train-rows.jsonl --validation $O/val-rows.jsonl
local/bin/rwkv-lab corpus pack --rows $O/train-rows.jsonl --exclude bench/distill/exclude.jsonl --max-tokens 8128 --out $O/dataset/train
python3 bench/distill/tools/to_segments.py --rows $O/dataset/train/rows.jsonl --out $O/dataset/train/segments.jsonl
```

- `pack` 不覆盖已存在的目录：重建前先把旧的 `dataset/` 挪成 `dataset-prev/`，不要删。
- `to_segments.py` 之后必须跑 §8 M0 的片段分词校验（`rwkv-lab corpus segcheck`），**不一致行数必须为 0**。理由：`loss_spans` 是字符偏移，且训练片段起点必须含 `Assistant:` 后的空格；任一条不满足，训练目标就和推理分词对不上（v1.3 实测原样切会有 2073/2157 行不一致）。
- `wire_hash` 必须仍为 `707c67403b1b…`（`dataset/train/manifest.json`）；变了说明有人改了 System 或渲染器，整批作废。

## 7. 执行者容易悄悄搞砸的地方

1. **照抄样例或考题**：本文样例是新编的形态示意；workbank / p13 / bfcl-product 的场景、文件名、公司名、数值一律不得进题（§3 通用规定）。归因文档里列了 workbank 题号和内容，**那是考卷，不是出题素材**。
2. **M1 改写时顺手把判据改宽**：去掉契约后判据从精确匹配变成 `output_contains`，不得再加「或者 UNKNOWN」之类的兜底选项；值本身仍必须准确。
3. **M2 给「查不到」的题补一个答案**，或判据只写 `output_contains_any: ["UNKNOWN"]`：这两样都会把题变回 v1.2 的形态。
4. **M3 第 2 轮被老师调了工具也照收**：S5 必须按 `forbidden_tools` 丢掉；不要放宽判据去「救」路径。
5. **M4 的 `offered_tools` 写进了没在 work-v1 里的名字**（如 `web_fetch_url`）：render 会静默得到更小的清单。写完对照 `eval.WorkToolCatalogNames()` 检查。
6. **M5 删掉写后回读**以「节省调用」：那一次回读是要教的行为（§3.5）。
7. **M6 允许 `read_file` 整读后心算的路径通过**：`expect.max_calls.read_file: 1` 不能删；老师算对了也要丢。
8. **为提高通过率给老师加重试兜底或放宽 `max_steps`**：会把「绕了很多弯才做对」的路径收进来；预算照 workflow S4。
9. **重建数据集时直接删 `dataset/`**：`pack` 拒绝覆盖是故意的，旧产物挪成 `dataset-prev/` 留档。
10. **按字节切 `loss_spans`**：它是字符偏移；转换只用 `to_segments.py`。

## 8. 里程碑

| # | 内容 | 估时 | 验收（可运行） |
|---|---|---|---|
| **M0 阻塞** | 工具改造：① `classify_failures.py` 新增 `short_garbage` 类（非 PASS、无 runner error、终答 ≤20 字符、不含判分里的期望值、不是 UNKNOWN/DONE、**不是纯数字**——纯数字算答错，排在 `wrong_answer` 之前）；② 片段分词校验入库为 `rwkv-lab corpus segcheck <segments.jsonl>`（逐行比较片段分词与整段分词、检查训练片段前一片段以 `Assistant:` 结尾、输出不一致行数）；③ 确认 scorer 能否从句子里取数（§3.1 第 3 步的 `number_in_text`），不能就实现或改用 `output_contains`；④ `bench sweep` 增加 `p13` 套件（`--cases bench/holdout/p13 --tool-catalog work-v1 --file-tools lines --include-draft`，题数 60），闸门题数同步 | 0.5–1 天 | ① 对 `local/runs/bench-20261003-v13/` 跑：v13b-s688 三次应为 9 / 1 / 8、none 三次都是 0（2026-10-03 按此定义实测）；④ `bench sweep --suites p13 --dry-run` 打出正确命令；② 对 v1.3 `segments.jsonl` 报 0；**负向**：用原始 `loss_spans`（不前移空格）生成一份，必须报 ≥2000 行不一致 |
| M1 | b09：M1 改写 450 条终答 + §3.8 心算行剔除 + §3.9 封顶 | 0.5 天 | 改写后机械校验通过率与重放通过率分别报；两者都 ≥85%，否则先看改写提示；抽检结果贴报告；**负向**：把一条改写终答里的值改错，重放必须判失败 |
| M2 | b10 试跑：每类先出 10 题过 S2–S5 全闸门 | 0.5 天 | 每类 10 题的通过率与中文自然度抽查（每类抽 3 条贴进报告） |
| M3 | b10 放量 | 2–3 天 | §5 各指标逐项报，未达标的写原因 |
| M4 | b11 N10 扩量 + 打包 + 转掩码 + segcheck | 0.5 天 | segcheck 0 不一致；`wire_hash` 不变；§5 表全部填实际值 |
| M5 | 训练（用户在训练机执行）+ 评测 | — | 见 §9 |

M0 不做的代价：没有 `short_garbage` 计数，就量不出 v1.4 最想治的那个问题；没有 segcheck，掩码错位会安静地毁掉整批训练。

## 9. 训练与验收

- 训练：`bench/distill/train-1-3.sh` 的参数照用，数据换成 v1.4 `segments.jsonl`（脚本里的 sha256 同步更新）。lr 用 1e-2 一路即可（v1.3 两个 lr 无差别）；另一张卡可以跑 4 epoch 的同 lr 版本，看 workbank 是否还涨。
- 评测：先每个 checkpoint 单跑 workbank + bfcl-product + p13-holdout 筛一遍；前 3 名 + none + v13b-s688 各补到 3 次，按题合并做配对检验（做法同 [state-v13 REPORT](../evaluations/state-v13-20261003/REPORT.md) §3）。

| 指标（三次均值） | v13b-s688 | v1.4 要求 |
|---|---|---|
| workbank 干净 112 | 24.7 | 不低于 v13b-s688（配对检验不显著变差） |
| bfcl-product 60 | 30.0（中文 21.0） | ≥36（中文 ≥26），即回到 none（39.7 / 29.0）的噪声范围内 |
| p13-holdout | 未测 | 高于 v13b-s688 |
| `short_garbage` 次数 / run（workbank 干净 112） | 6.0（9 / 1 / 8） | ≤2 |
| `closeout_tool_call` / run（workbank 干净 112） | 22 | ≤12 |

## 10. 待拍板

1. M1 改写 450 条终答是否足够把纯值终答压到 ≤40%：按 v1.3 数字估算（2051 行里 1435 行纯值），450 条改写 + 150 行封顶（约 120 行是纯值）+ 1000 行新增（纯值 ≤20%）+ N10 净增 100 行（沿用来源形态，约 70% 纯值）后约 38%（1135 / 3001），离 40% 的线不远。若 M3 后实测仍 >40%，是加大 M1 的改写量还是降低封顶值？
2. M4 的「小清单」是否也要扩到写工具缺失（如只给读工具时请求删文件）：目前只放了 50 行在第三种清单里，可按需加量。
3. 另一张卡跑 4 epoch 是否值得：v1.3 workbank 到 3 epoch 仍在涨，但 bfcl 随训练下滑；v1.4 数据若修好了 bfcl，4 epoch 才有意义。
