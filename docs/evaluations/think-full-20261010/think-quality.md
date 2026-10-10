# think-full 思考质量分析（2026-10-10）

范围：`local/runs/bench-20261010-thinkfull/` 中 workbank k0/k1（T 组 = `g1k+think-full --wire nudge=think`，A 组 = `g1k`）为主，bfcl-product 为辅。k2 未跑完，未纳入。
脚本：`analyze_think.py`（`python3 -I analyze_think.py stats`，只读）；人工标注：`manual_labels.py`。

## 一、结论

1. **T 组的 think 大部分不是空转，但"想得像样"不等于"做得对"。** T 组 workbank 共 1094 个决策步（k0+k1）。16% 是未闭合（115 步循环复读 + 47 步把工具调用写在 think 里没闭合 + 8 步其他）；其余 923 个闭合步经分层抽样人工校正后估计：结果驱动 62%（R）、浅层复述题面后直接动作 19%（S）、有具体对象的取证计划 13%（P）、空转/复述规则 6%（E）。折算到全部 1094 步：R 52%、S 16%、P 11%、E 5%、未闭合 16%。
2. **真正有用的是"读完工具结果后收口"，不是第一步的规划。** 第一步 think 里 P 只占 39%、S 占 55%（n=31），且与 A 组自发 think 质量相近（A：P 38% / S 38% / E 25%，n=24）。T 相对 A 的增量全在后续步：T 后续步 100% 有 think，其中 R 占 87%（n=89）；A 后续步只有 2% 有 think（13/595）。T 胜 A 的 15 个 case-run 里，人工判定 9 个 think 确有因果（失败后换工具、读结果后算出答案并停手），4 个是答案格式更干净，2 个是侥幸（cfg-0012 没查就答 UNKNOWN 恰好正确；fs-0012 把 write_file 循环了 10 次覆盖文件但终答碰巧对）。
3. **推理与动作不一致很普遍，集中在"失败后重试"。** 人工抽样 120 步中 16%（19 步）带 X 标记（想的和做的不一致）；第一步 0/31，后续步 19/89（21%）。典型是 think 写"换个更具体的查询"，下一个调用与上一个逐字相同；规则统计 result_fail 类 think 之后 41% 的工具调用是对同一 turn 内已出现调用的重复（plan 类仅 6%）。另有 12%（14 步）含事实/工具错误（W），如在读文件前就写"I have the config file showing …: 30"。
4. **想对了没做对：275 个失败 T case-run 中有 21 个（7.6%）think 里已有正确答案。** 其中 14 个最终输出也含正确值但被答案契约判负（带解释句、`/workspace/` 前缀、`**429**`、用了不该用的工具）；4 个答案在 think 里但终答因未闭合/JSON 解码失败/契约桩而丢失；3 个被工具结果覆盖（nt-0009 的 think 算出 24，随后把修复提示里的示例表达式 `4500*0.082*30/365` 原样抄进调用，得 30.33）。这是微调最该吃的一类。
5. **think 内容与成败只有弱的、被混杂的相关。** 21 个 T 通过里 9 个是 notool 类。去掉 notool 后（通过 12 / 失败 260）：think 引用了工具结果里新实体的 case-run 占比 75% vs 33%（Fisher p=0.005，但通过题步数更多、本身读了文件，相关不等于因果）；think 平均长度、重复调用率、是否出现循环均无显著差异（循环：42% vs 30%，p=0.52）。含至少 1 个未闭合步的 case-run 通过率 8/114 = 7%，不含的 13/182 = 7%，完全一样。失败的主要原因是答案契约与协议（启发式分桶：契约桩 89、答案裹在句子里 80、协议错误 63、真正值错/缺内容仅 39，共 281）。

## 二、方法

- 数据：summary.json 的 `turns[].result.steps`（与 trace.jsonl 的 model_call 一一对应，520/574 步），含 model_output、prompt、工具结果。think = `>` 之后到 `</think>` 之前；无 `</think>` 记为未闭合。A 组取 `<think>…</think>`。
- 规则分类（`classify`，按优先级）：
  1. degenerate：未闭合且（句子重复率≥35% 或 zlib 压缩比<0.12，或字符/词重复串）；
  2. unclosed_call（think 内出现 `<tool_call`）/ unclosed_long / unclosed_other；
  3. result_value：有前序工具结果，引用了"结果里有而题面没有"的实体、数字、或做了计算/比对，且未提失败；
  4. result_fail：前序结果失败/为空（或 think 自述失败），并据此调整；
  5. plan：提到题面实体/文件/工具且有理由词或枚举步骤、复述度低；
  6. shallow：复述题面 +"Let me start by exploring/reading"；
  7. recite：大段复述题面/系统规则/工具清单。
- 其它规则标记（repeat 与人工 X 对照：重合 13，仅规则 6，仅人工 6）：repeat（调用与同 turn 先前调用逐字相同）、ungrounded（路径是绝对路径或不在案例文件/结果/题面中）、notool_claim（"没有工具可…"）。
- 人工复核：
  - T 组 workbank 闭合且非循环步，固定种子（20261010）抽 120 步（占 923 的 13%），逐条读 think + 前序结果 + 后续动作，标 R/P/S/E 与 X（想≠做）、W（事实或工具错误）。
  - 另抽读 26 个未闭合/循环步，规则类别无一误判（13 个调用写进 think、13 个循环）；子类"循环前是否已算出答案"只读了其中几例，未逐条校验。
  - A 组闭合 think 抽 24 步（种子 8）。
  - 15 个 T 胜 A 的 case-run 全部逐步读了 T 与 A 的轨迹。
  - 33 个"think 含期望答案串"的失败 case-run 全部逐条读，其中 21 个确认。
  - bfcl irrelevance 首步 think 读了约 20 条。
- 规则 vs 人工一致率：把 result_value/result_fail→R、plan→P、shallow→S、recite→E，120 步中一致 92（77%）。分层看：result_* 合计 96%（66/69）；plan 仅 41%（11/27，其余为 S 6、R 5、E 5）；shallow 64%（14/22）；recite 2 条太少。所以 R 的比例可信，**P/S 的边界不可信**，报告里的 P/S 比例用的是"规则层 × 人工比例"的分层估计，不是规则直出。
- 局限：单人标注，没有第二标注者；P 与 S 的界线本身主观（我把"枚举了多步计划/带理由的查找"算 P，"复述题面+去探索/读文件"算 S）；通过的 case-run 只有 21（k0 11 + k1 10），任何通过/失败对比功效极低；bfcl 题面是中文，英文规则对其不可靠，bfcl 只做了定性。

## 三、思考内容分类（任务 1）

### 3.1 数量

T 组 workbank k0+k1，1094 步：

| 规则类别 | 步数 | 占比 | 人工校正后的归属 |
| --- | --- | --- | --- |
| result_fail | 306 | 28% | 96% 为 R（读失败/空结果后调整） |
| plan | 213 | 19% | 41% P，其余 S/R/E 混杂 |
| result_value | 196 | 18% | 93% R |
| shallow | 186 | 17% | 64% S，14% P，23% R |
| degenerate（未闭合循环） | 115 | 11% | 抽读 13/13 确认 |
| unclosed_call（调用写进 think） | 47 | 4% | 抽读 13/13 确认 |
| recite | 22 | 2% | — |
| unclosed_other / long / empty | 9 | 1% | — |

按用户给的四类归并（占全部 1094 步，估计值）：

| 类别 | 估计占比 | 说明 |
| --- | --- | --- |
| 有实质推理（R+P） | 63%（R 52% + P 11%） | R 中约 61% 是"失败/空结果后调整"，39% 是"读到具体值后计算/比对/收口" |
| 复述/空转（S+E） | 21%（S 16% + E 5%） | 另有 11% 的步是循环复读，也属空转，合计约 32% |
| 推理与动作不一致 | 抽样 16%（19/120，95% 区间约 10–24%） | 与上面各类叠加，不互斥 |
| 写了答案/调用却没闭合 | 4.3% 调用写进 think；另有 13 步（1.2%）未闭合且 think 里已写出"答案是…" | 13 步中仅 3 步的答案与期望一致 |

按步类型看（T 组）：第一步 301 步里 plan 130、shallow 96、unclosed_call 36、degenerate 34；常规后续步 424 步里 result_value 179、result_fail 152、degenerate 32；cutoff 重试步 111 步里 27 步又循环；forced（强制收尾）步 94 步里 52 步是 result_fail、17 步循环。

代价：未闭合/循环步只占 16% 的步数，但消耗了 **78% 的生成字符**；cutoff 重试 111 次，其中 79 次恢复成合法闭合动作（71%）。

### 3.2 各类原文片段（均 ≤300 字）

**R 结果驱动（好的）**
- web-0009 k0 step5：`The web_fetch result lists KG-4021 as "sealbreak" with the condition name "sealbreak". … The document says "sealbreak". The answer is "sealbreak".`
- fs-0001 k1 step2：`We have a list of files with sizes: README.md (280), exports/chain_wide_totals_2026-08.csv (497), … The largest is 497 bytes. So answer: 497.`
- log-0016 step4：`The read_file call failed because the path was absolute. I need to use a relative path. The file is at telemetry/docs/escalation.md, so I should use path: "telemetry/docs/escalation.md".`（这是"复述错误信息"，算 R 但信息量低）

**P 取证计划**
- tab-0007 step1：`I need to: 1. Read the roster to get worker information 2. Read the pick log … 3. Filter for June 2026 4. Filter for the Picking department 5. Calculate the average hours per worker. Let me start by reading the roster and the pick log.`
- fs-0002 step2：`I should search for files related to "watch-history" or "viewer" or "retention" or "records schedule".`
- log-0001 step1：`Likely logs are in a directory like logs/ or logs/checkout/. We need to search for "ERROR" entries.`

**S 浅层复述 + 直接动作**
- log-0017 k0 step1：`The user wants me to find the module that emitted a FATAL entry in the logs/claimdesk-api.log file. Let me start by reading the file to see what's in it.`
- scr-0004 step1：`The user wants me to rebuild a monthly settlement report. Let me start by exploring the project root to understand the structure and find the relevant files.`

**E 空转/复述规则**
- tab-0003 step2：`The user asks: "Trailcrest Outfitters' ordering system writes completed orders into a monthly export; … Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN." We need to answer with only the final answer…`
- cfg-0012 k1（该题通过，但靠的是这段）：`We need to answer based on the evidence we have. The user says "The route-planner service is coming up for its onboarding review. …" We need to determine which keys the settings file does not declare. But we have no evidence …`（多次整句引用题面，随后得出 UNKNOWN，从未调用任何工具）
- 循环（doc-0010 k0 step2，21357 字符）：`… The document does not specify the time window. The document does not specify the time window. The document does not specify the time window. …`

**X 想的和做的不一致**
- doc-0006：`The search results are not showing the repository. Let me try a more specific search.` → 实际调用 `web_search {"query":"anvil-relay github repository"}`，与上一次完全相同。
- code-0010：`The read_file call failed because the path argument was absolute. The schema requires a relative path. I'll retry with a relative path.` → 调用的 path 仍是 `/app/billing/notices.py`。
- tab-0007：`… There is no June 2026 hours data in the workspace. I cannot determine the average hours per worker.` → 下一步却又 `list_files {"path":"/home/node/.openclaw/workspace"}`。
- bfcl_irrelevance_5 k0：`This is a straightforward math question … I don't need to read any files or search for anything.` → 后接 `<tool_calls>[{"id":"call_…","type":"function"…`（首步 irrelevance 里 think 说直接答、却输出工具调用的，T 4/28，A 2/33）。

**W 事实或工具错误**
- cfg-0011 step2（k0、k1 各出现一次）：`I have the config file showing dispute_hold_minutes: 30. I should answer directly with that value.` → 文件此时还没读过，该值是凭空写的。
- tab-0017 step3：把 `MRA-2160: $62,340.00` 排成 "fifth largest"、把 `MRA-2041: $48,950.00` 排成 "third largest"，终答 MRA-2041（期望 MRA-2160）。
- log-0006 step3：`There is no tool to query a database or count lines in a file.`（read_file / search_text 都在工具清单里）
- nt-0012：`I should use the send_message tool …` → 调用了一个工具清单里不存在的 send_message，并编造了收件地址。

**未闭合且调用写在 think 里**
- nt-0008 k0 step1：`SHA-256 produces a 256-bit hash. Each hexadecimal character represents 4 bits … So, 256 bits / 4 bits per hex character = 64 hexadecimal characters. I can use the calculator tool to verify this calculation. <tool_call>{"name":"calculator","arguments":{"expression":"256/4"}}`（没有 `</think>`，答案 64 是对的，被判协议错误；cutoff 重试再次犯同样的错，该题 k0 失败，k1 重试后通过）

## 四、思考与结果的关系（任务 2）

### 4.1 T 胜 A 的 case-run（逐条读轨迹）

T-k0 比 A-k0 多过 8 题，T-k1 比 A-k1 多过 7 题（反向只有 A-k0 独有 nt-0004；k1 里 nt-0004 两组都过）。人工判定：C = think 确有因果，F = 主要是终答格式更干净，L = 侥幸。

| case-run | 判定 | 要点 |
| --- | --- | --- |
| doc-0001 k0/k1 | C | 先 web_search 为空；think：`The search did not return a specific meeting document. I need to locate the meeting document in the workspace.` → list_files → 找到文件。A 首步猜了 `/home/node/...` 路径，最终无有效终答 |
| doc-0005 k0 | C | list_files 目录不存在后 think 换 search_text，再读 CHANGELOG 得 4.6.0；A 重复同一 web_search 到被判重复 |
| fs-0001 k0/k1 | C | think 里对 list_files 返回的 5 个大小逐个比较，得 497；A 两次首步都陷入循环 |
| log-0017 k0/k1 | C | 读完日志后 think 抽出 `module=policy-renderer` 直接答；A 改用 search_text 并给出不存在的参数，被判重复后强制收尾 |
| web-0009 k0 | C | 抓取到页面后 think 写出 `The answer is "sealbreak"` 并收口；A 在后续查询里已经写了 sealbreak 却继续 web_search |
| tab-0010 k1 | C | 步 4 在 think 里逐行比较 10 行 units 与 reorder_point，数出 6；A 首步写了一段话+调用，被判契约违规 |
| code-0005 k0 | F | T 终答 `passed`；A 的 no_tool 理由里写了 "9 tests passed and 1 test failed"，被归一化后不等于 passed |
| nt-0006 k0 | F | T 直接答 429；A 去 web_search 后输出乱码 |
| nt-0007 k1 / nt-0008 k1 | F | 无需工具；A 的终答带 `<answer>` 包装被判契约违规，T 直接给出短答 |
| fs-0012 k0 | L | think 在 10 步里重复"答案是 release/manifest/crew-pairing-eu.csv"，同时对该文件 write_file 覆盖了 10 次（副作用），终答碰巧在允许集合里 |
| cfg-0012 k1 | L | 期望答案恰为 UNKNOWN；T 的 think 是对题面的整句复述，没查任何文件就答 UNKNOWN |

汇总：9 个 C、4 个 F、2 个 L。C 类的共同点只有两种形态：**失败/空结果后换策略**（doc-0001、doc-0005），**读到证据后算出或抽出答案并立刻收口**（fs-0001、log-0017、web-0009、tab-0010）。"首步规划"一个都没起到决定作用。

### 4.2 通过与失败 case-run 的差异（T，k0+k1 共 296 个 case-run，通过 21、失败 275）

全部 case-run，括号为去掉 notool 类后（通过 12、失败 260）：

| 指标 | 通过 | 失败 |
| --- | --- | --- |
| 步数均值 | 3.5（4.9） | 3.7（3.7） |
| 结果驱动步占比 | 0.30（0.44） | 0.29（0.29） |
| 其中 result_value 占比 | 0.18（0.24） | 0.11（0.11） |
| 未闭合/循环步占比 | 0.14（0.12） | 0.18（0.18） |
| think 长度中位数（字符，按 case-run 取中位再平均） | 1357（2071） | 2058（2099） |
| 后续步引用了工具结果新实体的步占比 | 0.39（0.51） | 0.21（0.20） |
| 重复调用占比 | 0.04（0.07） | 0.08（0.08） |

检验（去 notool）：有 ≥1 步引用新实体：通过 9/12，失败 87/260，Fisher p=0.005；出现循环：5/12 vs 78/260，p=0.52；有重复调用：2/12 vs 67/260，p=0.74。T 通过题按类别：notool 9/24、docs 3/24、filesystem 3/22、logs 2/34，code/config/tabular/web 各 ≤1，hybrid、script 为 0。

解读：只有"引用了工具结果里的新值"和通过相关，但通过题步数多、读了文件，这条相关里"读到了文件"是更直接的原因；循环、长度、重复调用与成败无显著关系。含未闭合步的 case-run 通过率 8/114，不含的 13/182，都是 7%。失败的主因不在 think 的好坏，而在答案契约与协议（启发式分桶，281 个失败 turn：契约桩 89、答案裹在句子里 80、协议错误 63、值错或缺内容 39、其它 6、空输出 4；A 组：协议错误 128、契约桩 80、裹句子 37、空输出 23、值错 17）。

### 4.3 think 类别与后续动作

T 组带工具调用的步里，按该步 think 类别统计：

| think 类别 | 工具调用数 | 与同 turn 先前调用重复 | 调用成功（ok=true） | 路径无依据 |
| --- | --- | --- | --- | --- |
| plan | 135 | 6% | 64% | 26% |
| shallow | 122 | 18% | 67% | 21% |
| result_value | 146 | 20% | 69% | 25% |
| result_fail | 230 | **41%** | 66% | 9% |

"针对失败做调整"的 think 最多，但落到动作上最容易原地重复；调用成功率各类相近（64–69%），即 think 的类别几乎不预测下一个调用能否执行成功。路径无依据（绝对路径 `/home/node/.openclaw/workspace/...` 或不存在的目录）在 plan 类最高，think 里写的是"先读 X"，X 是训练残留的路径而不是题面给的相对路径。

## 五、失败题里"想对了没做对"（任务 3）

自动串匹配（期望值/期望串出现在某一步 think 里，且不是题面里本来就有的）在 T 组 201 个可检查的失败 case-run 中命中 33 个；逐条读后确认 **21 个是真的**（其余 12 个是日期、数字、乱码里的偶然命中，如 code-0011 的乱码循环、fs-0004 的 "9"）。21/275 = 7.6%（占可检查的 201 个的 10.4%）。A 组同法命中 12 个，未逐条核查，不下结论。

| 类型 | 数量 | case-run | 说明 |
| --- | --- | --- | --- |
| F 格式/契约 | 14 | code-0009 k0, fs-0002 k0, fs-0010 k0, nt-0002 k0/k1, web-0014 k0/k1, web-0016 k0, cfg-0001 k1, doc-0005 k1, web-0013 k1, nt-0005 k1, nt-0006 k1, nt-0010 k1 | 终答含正确值，但带了解释句、`/workspace/` 前缀、`**443**` 加粗，或在不该用工具的题上调了 calculator。think 里本来写着 `Reply with only that path`，终答没执行 |
| G 答案在 think，终答丢失 | 4 | tab-0010 k0, doc-0002 k1, nt-0008 k0, nt-0005 k0 | tab-0010：think 逐行数出 6，随后输出了 `{"ok":true,"tool":"no_tool","result":{…"final_answer":"6"}}` 形状的假 tool_response，被判契约违规；doc-0002：think 得出 45 days，工具调用 JSON 里含裸换行，解码失败；nt-0008/nt-0005：答案或计算在 think 里，未闭合就走到调用或循环 |
| H 被工具结果覆盖 | 3 | tab-0019 k0, nt-0009 k0/k1 | tab-0019：think 逐个转换 13 个日期、数出 8 个，终答却采用 data_query 返回 0 行的结论写"0"；nt-0009：think `retry_limit 8 * 3 upstreams = 24`，calculator 参数被拒后，think 改写成 `The expression should be "4500*0.082*30/365"`——这是 harness 修复提示里的合法调用示例，被原样抄入，得 30.33 |

补充几条与 harness 相关的发现：
- 修复提示里的示例值（`4500*0.082*30/365`）在 T 组被逐字复制了 3 次（nt-0009 两次、tab-0002 一次），均导致失败，A 组 0 次。
- 失败后 think 里的"恢复计划"多数是对的（绝对路径→相对路径、`url`→`urls`），但绝对路径又被复写出来的情形也不少（见 X 的例子）。

## 六、多步任务中是否利用上一步工具结果（任务 4）

harness 在常规步里把历史步骤的 think 剥掉：T 组 1094 个 prompt 中仅 12 个在历史段含 `<think>`（都是 cutoff/invalid 的修复提示里原样带回）。模型每步只看见工具结果，下面的统计针对 T 组后续步（常规 + 工具错误重试，有前序结果）：

- 引用了前序结果里"题面没有的实体/数值"的步占 40%（232/574）；用到"反思前序结果"措辞（shows/returned/failed/empty…）的占 58%。
- 以"The user …/We need …/The question …"重新复述题面开头的 44/527 = 8%；完全没引用结果的"从头规划"仅 3%。
- 只引用**更早**几步结果（不在最近一步里）的实体：65/370（18%）——说明模型会把更早的工具结果带进当前判断，但主要还是盯着最近一步。
- 已给出终答的 164 步里，有 55 步（34%）think 里已经把最终答案原文写过一遍，终答只是抄一遍。

结论：think 不是每步重新规划，而是**对最近一次工具结果做一两句话的反应**（中位数 281 字符），这既是它的优点（便宜、跟随证据），也是缺点（不做跨步骤的整体计划，失败后原地重试 41%）。

## 七、A 组自发 think 与 T 组对比（任务 5）

| 指标（workbank k0+k1） | A | T |
| --- | --- | --- |
| 带 think 的步 | 352/1209（29%） | 1094/1094 |
| 首步带 think | 273/300（91%） | 302/302 |
| 后续步带 think | 13/595（2%） | 575/575 |
| 首步 think 闭合率 | 78% | 76% |
| 首步 think 中位长度（字符） | 389 | 354 |
| 首步类别（规则） | plan 142, shallow 70, 循环 30, unclosed_call 28 | plan 130, shallow 97, unclosed_call 36, 循环 34 |
| 全部 think 中循环 / 调用写进 think | 15% / 10% | 11% / 4% |
| 人工首步标注 | P 38% / S 38% / E 25%（n=24） | P 39% / S 55% / E 6%（n=31） |
| 自述"没有工具可…"的首步 | 4% | 4% |

要点：
1. **A 的自发 think 基本只发生在第一步**（91% vs 后续步 2%）。所谓"约 30% 步骤自发思考"，实际是"几乎所有首步 + 几乎没有后续步"。
2. 首步 think 质量两组相当：闭合率、长度、类别分布差不多；T 的预填没有让首步想得更好，也没有让它更差。A 的 24 条样本里 E 偏高（6/24，含 4 条"no tool available → UNKNOWN"的错误断言和 1 条把 harness 的 cutoff 提示当题目复述），但样本太小，不能当显著差异。
3. A 组带 think 的步协议错误率 24%（68/284），不带 think 的步 2%（9/466）；说明 A 里"自发 think"是和未闭合绑定的风险源，T 通过预填 `<think` 把这个风险变成固定成本（每步 16% 未闭合），换来了后续步的结果驱动 think。
4. 两组都有的"想的是 A 做的是 B"：A 在 24 条里标出 1 条 X、6 条 W；T 首步 0/31 X、2/31 W，后续步 19/89 X、12/89 W。X 之所以集中在 T 的后续步，是因为 A 后续步根本不想，没有可以不一致的 think。
5. 重复调用（同一 turn 内逐字相同）：A 40% vs T 25%（占各自的工具调用步）；A 更常陷入"同一调用重发到被判重复"，T 因为 think 里至少承认了结果而少一些，但仍有四成的失败后重试是重复。

## 八、bfcl-product（辅，定性）

- T-bfclp k0/k1：irrelevance 11/20、5/20，missing-required 16/20、16/20，multiturn 16/20、14/20；A-bfclp k0/k1：irrelevance 11/20、10/20，missing-required 16/20、18/20，multiturn 11/20、14/20。T 在 multiturn 上略好，在 irrelevance 上波动大（k1 掉到 5）。
- 题面是中文，think 多为中文，规则分类对其不可靠（"recite"占 18–20% 主要是规则对中文失效），不做定量。
- irrelevance 首步（T 28 个闭合 think）：think 明确说"直接回答/不需要工具"且没调工具的 11/11 通过；think 说直接答但输出了 `<tool_calls>…` 的 4 个全部失败；think 里没说直接答而去调工具的 9 个全部失败。A 同样：17/17、2 个不一致失败、10 个调工具失败。**在 irrelevance 上，think 的结论与成败强相关，一致性是关键**。
- 多轮题（read facts/xxx 类）的 think 都是"先 list_files 确认文件存在再 read"这类短计划，未发现空转。

## 九、给"带思考的 MiSS 微调"的数据建议

可保留（做训练样本）：
1. **读完证据后收口**：think 逐项抽取/比对/计算（如 fs-0001 比较大小、tab-0010 逐行比较、log-0017 抽模块名），`</think>` 之后立刻给出**纯值终答**（无解释句、无路径前缀、无加粗）并带 EOS。这是 T 胜 A 的主要来源，也是 G/F 类失败的反面教材，数据量应最大。
2. **失败/空结果后真的换策略**：think 指出原因 + 下一次调用与上一次**参数不同**（目录不存在→search_text / list 上一级；web 路径→web_fetch；绝对路径→改成题面给的相对路径，且调用里确实是相对路径）。
3. **不需要工具时的直接作答**：think 里算出/回忆出答案并明确"no tool needed"，终答是裸值（nt 类，T 的 nt-0006 就是这样赢的）。
4. **带理由、对象是题面里存在的文件的取证计划**（P）：保留短的（≤ 600 字符）、对象来自题面或前序结果的；第一步 think 本身对成败帮助不大，不要在这类上堆量。
5. think 长度分布：中位 250–350 字符的短 think 是主流，长于 ~1500 字符的闭合样本很少且大多是在抄表，不必刻意保留。

必须过滤：
1. 一切**未闭合** think（循环复读、`<tool_call` 写进 think、think 里写完答案就 EOS）；规则：无 `</think>` 即丢，另加句子重复率 ≥ 0.2 或 zlib 压缩比 < 0.2 即丢。
2. **X 类**：think 里写"换更具体查询/用相对路径重试/无法确定"，动作却与此矛盾。可程序化筛：think 含 "different/more specific/broader" 且调用与同 turn 先前调用相同；think 含 "relative path" 而 path 以 `/` 开头；think 结论是 UNKNOWN/cannot determine 而下一步仍调工具；think 说"直接回答"而输出里有 `<tool_call`/`<tool_calls`。
3. **W 类**：think 在读文件前就宣称"I have the file showing …"；"没有工具可…"而工具清单明明有；引用不存在的工具（send_message、search、read_files、count_lines_in_file）；把部署时间当 ERROR 时间之类的推理错。可程序化筛：think 中出现的实体既不在题面也不在已有工具结果里的数值（`derived`）且最终被采用时，要求有计算依据；工具名必须在 `tools_offered` 内。
4. **复述题面/规则/工具清单**（E）和"复述题面 + Let me start by exploring"（S）：不含信息，保留会教模型"想什么都不重要"；只在极短（≤ 120 字符）且紧接合法动作时少量保留。
5. **强制收尾（forced）与 cutoff 重试步里的 think**：它们是在 harness 的补救提示下生成的，常整段复述提示（"Your previous reasoning never finished…"），不要当作正常样本。
6. **含修复提示示例值的样本**：若 think 或调用里出现 harness 示例表达式（如 `4500*0.082*30/365`）而题面不含，丢弃；同时建议 harness 把修复提示里的示例换成不可能被抄用的占位或移除。
7. 靠侥幸通过的样本（cfg-0012 这类"没查就 UNKNOWN"、fs-0012 这类循环 write_file 后碰巧答对）不能因为 `passed=True` 就入库，必须同时通过上面的一致性筛选。

训练格式提醒（承接 `docs/evaluations/g1k-wire-ablation/07-think-fast.md`）：本数据再次证明"答案写在 think 里没闭合就 EOS"在 T 组仍然存在（47 步调用写进 think + 13 步未闭合时 think 里已有结论）；训练目标必须是 `think → </think> → 恰好一个动作（或裸终答）→ EOS`，终答的 loss 要覆盖结束符。

## 十、可信度与未做的事

- 把握较高：循环/未闭合的占比与代价（规则确定、抽读全中）；R 类占大头且集中在后续步；T 的首步 think 不比 A 的好；A 的 think 几乎只发生在首步；"想对了没做对"至少 21 个且以格式/协议类为主；X 与 W 在失败后重试里很常见。
- 把握中等：P 与 S 的比例（规则一致率仅 77%，plan 精度 41%，靠分层抽样估计）；X 16%（n=120，区间 10–24%）；T 胜 A 的"因果"判定（15 个 case-run，单人判断，且 A 与 T 走的是不同路径，无法做严格反事实）。
- 把握低：通过/失败的统计对比（通过仅 21 个，其中 notool 9 个，Fisher 检验功效很低，p=0.005 的那一项还被"读了文件"混杂）；A 组 24 条样本的比例；bfcl 的定量结论（中文题面，规则失效）。
- 未做：k2 与 F-* 组；A 组"think 含正确答案"命中的人工核查；第二标注者的一致性；对每个循环步"循环前是否已算对"的逐条核查。
