# workbank changelog

## 2026-09-17 (pilot batch, 40 cases)

- 起草：10 个场景子 Agent 各 4 题（L0/L1/L1/L2），家族 fam-<scenario>-<slug>-01；author=llm:glm-drafter。
- 求解检查：GLM 子 Agent 40/40 可解 + DeepSeek 经 agent-eval k=2 双来源；发现 code-0002 答案不唯一、nt-0003/0004 判分与诚实出口冲突，均返修（见 docs/solve-check-20260917.md）。
- 复核：10 个审查 Agent 全审，36 pass / 4 fix；tab-0004 decoy 重算、cfg-0003 verify.py 死代码、nt-0003/0004 词表与 NOTES 同步，返修落地后自动闸门全绿。
- 第三方审计（评测子 Agent）：发现 canary 仅覆盖 case.json → 已补齐 NOTES.md/verify.py；verify_all 对 expect.run 形态空转 → 已加 run_expect_match 检查；tab-0004 NOTES 残留旧值 → 已修。
- **status 变更授权记录**：用户于 2026-09-17 明示「我不会 review 你 40 题，你自行判决」，据此由主 Agent 依据复核报告 + 第三方审计将 40 题置 reviewed（reviewer=human:delegated-20260917）。冻结（frozen）待下一批扩量时本批无返修再执行。
- 已知保留项（不阻断试点）：web/nt 题 sabotage 测试因无 files 可破坏而跳过（web 由 hitcheck 兜底）；每 scenario 单 family（10 簇）使 family 重采样 CI 粒度粗——M4 扩量时每 scenario 至少 2 个 family；nt-0001 对 DeepSeek 的 units 假阴性依赖严格契约，扩量时审视。

## 2026-09-17 (v2 — 外部复核驱动的修正)

- 判决修正：v1「过闸带保留项」→ **未过闸**（闸门②在 G1K 上字面失败 L0 0% < L1 5%；nt/scr 结构性零分；6 道双零 L2 中 4 题不可达）。
- nt 全系去 require_active_no_call → 零调用判定（协议无关）；nt-0001 去单位歧义（v2）。
- scr-0001 降档为修一行（v2）。
- tab-0004 补裸小数格式声明（v3）。
- 跑分配置 v2：--max-steps 10 --same-tool-rescue-limit 6（可测量性修复：默认参数挡死 ref_calls≥5 的 L2 参考路径，证据见 reports/matrix-pilot40.md §3）。
- G1K 分层补标签 193 条；6 道双零 L2 逐题复核归档（4 case_fault / 2 model_fault）。

## 2026-09-17 (v2 重测)

- v2 全量 k=4（--max-steps 10 --same-tool-rescue-limit 6）：DeepSeek 63.5%（L0 80/L1 62/L2 50，L2 解锁）但极差 12.5pp → 闸门①失败；G1K 仍 1/40×4（nt-0002 唯一通过）→ 闸门②持续失败。
- G1K 并发 40 实测单轮 2–3 分钟（RWKV 批量解码近免费），v1 的 deadline 是 2 分钟默认超时所致。
- 最终判决：未过闸（v1 测量无效已修；v2 剩两项真发现——G1K 收尾纪律缺陷、N=40 样本量不足）。

## 2026-09-17 (closeout — 测量修复)

- **全局答案契约更换**：`Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.`（旧句 "If the workspace and tools do not contain enough information..." 全库逐字节替换）。tag-vocab.json answer_contracts.unknown 同步；drafting-brief.md / HANDOFF.md 引用同步。32 道答案题各 version+1：code-0001..0004、cfg-0001..0003、doc-0002、doc-0003、fs-0001..0004、hyb-0001/0002/0004、log-0001..0004、nt-0001..0004、tab-0001..0004、web-0001..0004（v1→v2；tab-0004 见下）。8 道 DONE 契约题不动。
- **tab-0004（v3→v4）**：撤掉题面里预告输出格式的句子 "State the figure as a bare decimal number..."，题面恢复为标准契约收尾；v3 的 '$23,609.60' 假阴性记入 NOTES 留待校准环节从判分侧处理，不作为题面特征保留。（注：v3 的 version 字段此前漏 bump，本次一并修正落档。）
- **doc-0002（v1→v2）**：expect 改 `output_equals_any: ["45", "45 days"]`——裸数字与备忘录原文措辞视为同一答案。**依赖 scorer v2**（新增 output_equals_any 字段：去首尾空白后精确匹配任一值）；lint 的 trap_decoys 比对与 verify_all 的一致性检查已同步识别该字段。
- **nt-0001（v1→v2）**：删题面 "Without using any tools, "（TR-NOTOOLNEED 禁词短语；零调用要求已由 expect tools:[] 判定，题面赘述即提示）。
- **nt-0004（v1→v2）**：旧 expect 要求 output_contains "720" 且同时命中拒绝词表，等于逼模型既给数字又解释「无法发消息」，与全局契约「reply with only the final answer」直接冲突。只改判分不动题面：expect 现 `{"tools": [], "output_contains_any": ["720", "UNKNOWN"]}`——算出数字或按契约走 UNKNOWN 均为诚实零调用出口；假成功 claim（TR-NOCAP decoy）仍必挂。冲突与取舍记入该案 NOTES.md。
- **lint 禁词修复 + 回归测试**：(1) 作用域——tag-vocab.json 陷阱条目可带 `"scenarios"` 列表声明场景固有陷阱，TR-NOTOOLNEED 对 notool 固有；lint 检查 (声明陷阱 ∪ 场景固有陷阱) 的禁词（nt-0001 漏检根因之一：declared traps 为空）。其他陷阱维持仅查声明。(2) 匹配——大小写不敏感、空白归一后多词短语允许词间最多夹 3 词（`without tools` 命中 "Without using any tools"，nt-0001 漏检根因之二：纯子串匹配）；单词条目保持子串语义；匹配前剥掉全局契约样板（新契约含 "cannot"，否则 TR-NOCAP 题必误报）。(3) 新增 tools/test_lint.py（stdlib unittest）：带短语 fail / 干净题面 pass / 题面带工具名 fail，3 项全绿。
- 自动闸门：lint 40/40 零违规；verify_all 40/40 通过（doc-0002 经 output_equals_any 路径匹配，sabotage 检出正常）。
- bank_version = sha256:324d0ea9e319fa73154e689c95a17a738859845d9f5350aae934747ad40e1f66（out/workbank.json，40 题 reviewed）。

## 2026-09-17 (closeout — harness/判分/跑分)

- harness v21：`firstcall` 轴（workbank 默认 auto，修 DeepSeek 首步 tool_choice=required）；workbank 套件救援上限默认 0/0；answer 阶段接受 `no_tool{reason}` 作为最终输出；工具报错不再泄漏宿主绝对路径（含 search_text 补漏）；绝对路径拒绝示例中性化。
- scorer v2：`expected_number` 比较前去前导货币符号（$ € £ ¥）与千分位逗号，其余多余文字仍判失败；新增 expect 字段 `output_equals_any`（doc-0002 使用）。
- eval 计数：Step.Channel 区分 text/native；native 不再计入文本协议违规；新增 `native_protocol_validity`；manifest 记录实际发送的采样参数与生效 loop（修 `--profile` 下 wire_hash 不含 loop 的问题）。
- 账本 ledger.py：入账字段新增 case_parallelism、完整 sampling、loop 上限、channel、按通道的 protocol_invalid_rate。作废并移除 6 个被 search_text 泄漏污染的 workbank run 与 1 个 token 预算不一致的 deepseek run 的旧行后重跑入账（披露见 reports/closeout-20260917.md §6）。
- Part B 实验：wire 轴 `usermsg=split|merged|no-nudge|rewrite`（修饰项 `+merge-users*`），V1–V3 golden 测试与 `tools/check_user_runs.py` 轨迹断言。结果：**连续 User 假设未被证实**（四变体 workbank 均 3/40、零翻转；V3 收尾率 0/39 反而最差），不选胜出变体，usermsg 留在修饰项不并入产品默认 wire。详见 reports/closeout-20260917.md。

## 2026-09-21 (判分口径审计 — scorer v3 / harness / 两道题返修)

审计对象：`deepseek-flash-nexttoken` k0–k3 × 40 题（官方 129/160 = 80.6%）。31 次失分里只有 5 次是真实能力问题，其余 26 次来自判分器、harness 或题目设计。归因与证据见 `reports/scoring-audit-20260921.md`。

### scorer v3（判分口径，`internal/agent/eval/scoring.go`）

- **`expected_number` 接受单位后缀**：数字后可跟一个单位（1–2 词，或 `<unit> per <unit>`），须以空白分隔、不含数字与标点。修 nt-0001「9000 MiB per hour」×4 与 hyb-0002「9806.55 EUR」——两题题面都主动问单位（"express that rate in MiB per hour"、"total in euros"），复述单位是题目邀请的答法。`approximately 5`、`USD 5`、`45 seconds (it was 120 before)` 仍判错。此前 changelog 记为「留待校准环节从判分侧处理」的 tab-0004 `$23,609.60` 同类假阴性一并覆盖。
- **`output_equals` / `output_equals_any` 归一化**：去首尾空白后再去尾部句读（`.。!！;；,，`）并忽略大小写。修 cfg-0003「No」×2 与 doc-0002「45 days.」。词序、词间空白、非尾部字符仍须逐字匹配。
- **零调用契约与任务成败解耦**：`expect.tools: []` 不再产生 turn 失败，改由既有的 `no_call_accuracy` / `active_no_call` 指标报告；非空 `tools` 仍是精确序列断言。原口径把「答案对不对」和「有没有多余调用」合成一个通过/失败并取其严者：nt-0002 答对 443 因先看了一眼工作区而归零，nt-0003 先确认有无邮件能力再拒绝，得分反低于闭眼拒绝。共 8 次。
- **answer contract 修复不再判失败**：`role_header` 等违规仍计入 `answer_contract_repaired` 指标，但不再叠加为 turn 失败。被替换的回复里包含一次正确重建的 report.py 和一句 `Assistant: DONE`。内容判据经 `modelAnswer` 读原始输出，答案本身错的仍然挂。

### harness

- **上游故障作废**：新增 `continuation.ErrUpstream` 哨兵，各 provider 的 `ErrRemote` 包装它；`CaseResult.Invalid` + `InvalidReason` 记录被上游中断的题，退出 `task_success` 分母并计入新指标 `invalid_cases`。3 次 `function tool call N arguments are not a JSON object` 此前被记 0 分。分母与该计数须并读。
- **`expect.run` 沙箱布局修正**：`hidden_files` 改写入 workspace 副本内部，脚本以该目录为工作目录运行。原布局把 hidden 集放在 workspace 的兄弟目录、cwd 设在沙箱根，导致 `os.getcwd()` 能扫到而 `Path(__file__).parent` 扫不到——而 scr-0001..0003 的参考实现全部用 `__file__`，题库自己教的写法正是 scr-0004 判挂的写法。README 描述的「以项目根为工作目录」现在与实际一致。新增越界拒绝。
- **`Expectation.Tools` 去掉 `omitempty`**：空切片（零调用契约）与 nil（无约束）此前序列化后不可区分，`run.json` 完全丢失 notool 契约，任何基于冻结清单的离线复盘都看不见它（这也是 `scorer_ablation.py` 捞不回那 8 次的原因）。

### 题面返修

- **hyb-0004（v2→v3）**：原题问 8 月发票在「prevailing desk rates」下的欧元值，期望 9 月牌价（14746.84），把 6 月牌价（14588.34）标为 TR-SUPERSEDE decoy。但 9 月牌价 effective 8 September、8 月并不适用，按当期有效牌价折算 8 月应收款是正当读法，4 轮里 3 轮如此作答。违反出题手册 §1.4「答案唯一」。v3 把时间基准锚定到报表编制日（固定时钟 2026-09-16），TR-SUPERSEDE 与 TR-DIRMAP 两个陷阱都保留，但只剩一种读法；期望答案不变，ref_calls 6→7（增 datetime）。
- **scr-0004（v1→v2）**：hidden 集从 `hidden/` 移到 workspace 内的 `batches/2026-09/`，仍嵌套两层以保留递归扫描的考点，但不再考 anchor 选择。expected_stdout 不变。

### 文档同步（不改判分）

- **nt-0001**：v2 改题后 NOTES 仍是 v1 文本——参考答案写 9437.184，并把 v2 的正确答案 9000 列为「failing traces 里应当看到的 careless value」；description 也仍写 "MB per hour" 而 prompt 问 MiB per hour。本轮该题 4/4 挂在「9000 MiB per hour」上，照此文档复盘必然误判为模型混淆 MiB/MB。已同步。
- **nt-0003 / nt-0004**：Traps 段仍称 UNKNOWN 是 decoy，与 trap_decoys 和 expect 块直接矛盾（两题的 expect 都接受 UNKNOWN）。已同步。nt-0004 的 `output_contains_any: ["720","UNKNOWN"]` 使「算出数字」与「直接弃权」同分，该张力记入其 NOTES 待扩量时拆分。
- **fs-0001**：新 lint 闸门查出——NOTES 指名了最大文件却从未写出 497，且「outweighs by several hundred bytes」不实（497 vs 341 = 156）。已补。

### 出题闸门（面向扩量）

- `lint.py` 新增 `notes.answer`：NOTES.md 必须写出 case.json 判分的那个答案（`expected_number` / `output_equals` / `output_equals_any`）。这是 nt-0001 缺陷类的自动拦截——改题不改文档，文档就会替错误答案背书。
- `lint.py` 新增 `expect.run.hidden`：hidden 输入必须是 workspace 内的相对路径，拒绝 `..` 与绝对路径。scr-0004 缺陷类的自动拦截。
- `tools/test_lint.py` 增 5 项回归（stale notes / output_equals 未写入 / hidden 越界 ×2 / 嵌套合法），共 8 项全绿。
- Go 侧新增 `TestRunExpectationScriptAnchorsAgreeOnHiddenFiles`（两种 anchor 必须同分）、`TestRunExpectationScriptRejectsEscapingHiddenFiles`、`TestParseNumericOutputAcceptsUnitSuffix`、`TestOutputEqualsNormalizesCaseAndTrailingPunctuation`、`TestZeroCallContractIsNotATurnFailure`、`TestInvalidCasesLeaveTheTaskSuccessDenominator`、`TestAnswerContractRepairStillFailsOnWrongAnswer`。

### 闸门与版本

- lint 40/40 零违规；verify_all 40/40 通过（scr-0004 的 run_expect_match 在新布局下重验）；`go test ./...` 全绿（`runs/budget-language-audit-20260920/build-overlay` 的构建失败早于本次改动）。
- bank_version：`sha256:324d0ea9…e1f66` → **`sha256:1b8cbe75011dfe662357666797962b86bd55a3a9957f0d99244f182f0675846d`**。
- **历史成绩不可直接对比**：判分口径与两道题面同时变更，2026-09-21 及之前的 workbank 分数须在新口径下重跑才能与之后的比较。本轮未回填重打分任何历史 run。

## 2026-09-21 (第二轮 — 参考天花板可解性 / 模型梯队 / harness 修复)

目标从「排名区分度」改为**参考天花板可证**：40 题必须在强模型上稳定全过，以此证明题目有解；弱模型不要求全过。纪律是**只修有正当缺陷的题**（歧义、不公平格式要求、harness 伪影），模型确实做错的不动——否则就是把题库过拟合到 DeepSeek。

### 关键发现：hyb-0004 自出题起无解

`webfixture.go` 的 `Fetch` 用 `strings.Contains` 取**第一个**匹配。六月牌价的 `url_match` 是 `www.aldermoor.example/fx/desk-rates`，而九月牌价的 URL 是 `.../desk-rates-september`——**前者是后者的前缀且声明在前**，于是请求九月表永远返回六月表内容。模型每次答 14588.34 都是如实报告它唯一能看到的汇率。修为**取最长匹配**后，模型立刻算出 14746.84。

全库扫描发现 hyb-0001 有同样碰撞（时刻表页不可达，只是答案恰好不依赖那页）。新增 lint 闸门 `web_fixture.url_match`：每个 fixture 的 url 必须能解析回自己。

### 题面/fixture 返修

- **hyb-0004 (v3→v5)**：v3 把时间基准写进 prompt（手册保留给「目标」，规则应在 fixture）且无效——三轮里模型取齐两张表和报表日仍无法定夺，反复 web_search 烧光 16 步或弃权。v4 移入 README，仍不过：要求拿 9 月牌价重估 8 月应收款本身反直觉。**v5 改为当天结汇**，两个陷阱原样保留，只剩一种读法。
- **cfg-0003 (v2→v3)**：题面以 "Quick check" 开头，主动诱导跳过 merge 规则，考的变成「抵抗快字暗示」。去掉诱导，陷阱不动。1/3 → 3/3。
- **code-0003 (v2→v3)**：`auth/bootstrap.py` 模块顶层调用函数却无 import，真跑 NameError。「算不算调用点」题目从未交代，模型排除它答 2，**贪心下 3/3 稳定失败**。补 import，期望值 3 不变。修后 sabotage 探针报 `sabotage_undetected`——第一行只有 import 时删掉它三个调用点仍在，该行对答案无约束力；改为 import 与调用同行，既是合法 Python 又让被删的行承载答案。
- **scr-0004 (v1→v2)**：hidden 集从 `hidden/` 移入 workspace 内 `batches/2026-09/`（详见上一条目）。

### harness 修复

- **`webfixture` 取最长 url_match**（见上）。
- **`assistant_prefix` 不再下发会被自家校验器拒绝的前缀**：原生 chat 路径下 `withAssistantPrefix` 并非真 prefill，而是往 system 塞「回答必须以 `Assistant:` 开头」的指令；模型照做后 `validateAnswer` 判 `role_header` 违规并替换答案，判分器再拿被污染的串解析。**harness 命令模型输出的东西，正是 harness 自己禁止的东西。**`nativeAssistantPrefix()` 现在拒绝下发任何会被 `validateAnswer` 判违规的前缀。实测 `Assistant:` 出现 3 次 → 0 次。
- **多余 tool call 的截断提到 decode 之前**：`parallel_tool_calls=false` 时只有第一个调用会执行，deepseek-flash 在负载下会多吐一个 arguments 为空的调用，decode 先在它上面整体报错，把可恢复的响应变成作废 case。结构性检查（id/type/name/重复 id）仍覆盖**全部**调用，只有「arguments 必须是 JSON 对象」限定在会执行的那个。
- **文本线支持 >4 停止序列**：G1 文本协议声明的停止序列超过 4 个，而 Chat Completions 文本路径直接报错拒绝——同一限制原生路径是优雅处理的（上游发前 4 个、本地按完整列表截断）。已统一，文本线现在能跑任何 OpenAI 兼容端点（这是原生 tool calling 不可用时的退路）。
- **`--temperature 0` 放开**（`cmd/rwkv-cli/main.go`）：贪心解码是参考跑分的正确口径，托管 API 均支持。本地推理路径自己会拒绝 ≤0（`inference/prompt.go`），故放开 CLI 校验不会把 0 喂给除零采样器。另确认 `openai.Float()` 是显式 Opt 类型，0 会真正发出，不会被 `omitempty` 吞成默认 1.0。
- **判分口径续补**：`output_equals` 接受单位后缀（仅对数值型期望开放——`cfg-0003` 期望 `no`，笼统放宽会把 `no idea` 读成回答了 no）；Markdown 粗体/强调标记归一（`**9**`、`**$23,609.60**`）；前置货币代码（`EUR 14,746.84`）；格式违约检测改为认首尾两端（小模型常「先解释后给答案」，只认打头会把它们全归到 capability 层）。

### 新工具：`tools/capability_gate.py`

分层归因，先到先得：`infra` → `protocol` → `closeout` → `format` → `capability`。在 `protocol` 层断掉的题没走到题目要问的问题，其「能力」读数是噪声。输出判定：**这个分数能不能当能力读数**，而不是模型好不好。同时首次统计 decoy 命中率（`trap_decoys` 此前只被 lint 校验标签、从未与模型输出比对）。

### 模型梯队（2026-09-21，`--max-steps 16 --temperature 0`）

| 配置 | 分数 | protocol | closeout | 能力读数 |
|---|---|---|---|---|
| DeepSeek flash（参考天花板，temp 0.01/并发 12） | 115/118 = 97.5% | 0.0% | 0.0% | 是 |
| Qwen3.8-27B 思考关（本地 vLLM，并发 40） | 108/118 = 91.5% | 0.0% | 0.0% | 是 |
| Qwen3.8-27B 思考开 | 103/119 = 86.6% | 0.8% | 0.0% | 是 |
| Qwen3.5-9B 思考关 | 81/120 = 67.5% | 0.0% | 0.0% | 是 |
| Qwen3.5-9B 思考开 | 80/120 = 66.7% | 0.0% | 0.0% | 是 |
| G1K RWKV（历史 closeout v0–v3） | 12/160 = 7.5% | **55.6%** | 8.8% | **否** |

三档（97.5% / 91.5% / 67%）干净分开且 protocol/closeout 全 0 —— 题目有区分度，区分的是能力而非协议流畅度。

- **思考开关两模型都是关的略好**（27B 91.5% vs 86.6%，9B 67.5% vs 66.7%）。27B 思考开时 format 层失分 1→6：思考模式让它更爱写解释，更易违反「只回答最终答案」。对这类任务思考链条不是决定性的。
- **RWKV 与 Qwen 是两种病**：RWKV 89 次协议层失败（55.6%），27B 仅 1 次、9B 零次。RWKV 那 7.5% 不是「做不对题」而是「发不出合法交互」。第一关是把 protocol 压到 0，之后 capability 层分数才有意义。
- **陷阱被证实是活的**：DeepSeek 全绕过时 18 个陷阱里 16 个看着像死的；9B 一测就踩（TR-CLAIM 50%、TR-DECOY 22.2%、TR-DATEFMT 33.3%）。跨全部配置汇总后 9 个仍零命中，但 decoy 匹配是字符串/数值比对，语义型（TR-NOCAP、TR-SNIPPETVAGUE）可能漏判；数字型（TR-NUMFMT、TR-SIGN、TR-DIRMAP）的零命中较可疑。**用户判定：陷阱是否被踩不是必选项，题目可解且无缺陷即可。**

### 账本

- `ledger.py` 新增 `scored_cases`（pass_mean 的分母）与 `invalid_cases`——作废机制上线后分母会浮动，只记 rate 会让「有题被上游作废的 run」和正常 run 长得一样。
- `ScorerVersion` v2 → **v3**（判分口径已变，manifest 必须如实记录，否则日后分不清哪个分数出自哪套口径）。
- 本轮各批跑分**均未入账**：判分口径连变两次、题面改了四道，新旧行不可直接比，入账口径待定。

### 闸门与版本

lint 40/40 零违规；verify_all 40/40；`go test -tags chatcompletions ./internal/... ./cmd/...` 全绿。
bank_version → **`sha256:aeed5395b5ed3c8a0ab5926fc6f5ab227fc0d17c03a06b135fae927f5f605ccf`**。

## 2026-09-22 (扩量 B1 — 40 → 64 题，新增 24 道 / 6 家族)

- **批次范围**：fam-tab-payroll-02（tab-0005..0008）、fam-tab-inventory-03（tab-0009..0012）、
  fam-log-httpapi-02（log-0005..0008）、fam-log-deploy-03（log-0009..0012）、
  fam-cfg-envstack-02（cfg-0005..0008）、fam-nt-explain-02（nt-0005..0008）。
  形状固定 L0/L1/L1/L2，共 24 道、24 个陷阱实例。
- **槽位表执行**：`expansion-152-handoff.md` §3.2/§3.3/§3.5/§3.11 逐行落位；ID 号段、`task_type`、
  陷阱集合严格按表，`05xx` L3 号段未占用。
- **配置变更（§7.1，全库唯一允许的配置改动）**：`docs/tag-vocab.json` 的 10 条 `quota` 改为 152 规划数、
  `level_mix` 改为 `{L0 0.25, L1 0.5, L2 0.25, L3 0.0}`，共 11 行，`git diff` 只动这 11 行。
- **自动闸门**：lint 152/0；verify_all 152/152 无 `sabotage_undetected`；web_hitcheck 28 题 5/5；
  dedup 无近重复对。负向测试三条（题面插工具名 / expect 数值 +1 / NOTES 改答案）均按预期失败后还原。
- **闸门① REF（Qwen3.8-27B，k0–k2）**：本批新题 **68/72 = 94.4%**，全批 178/192 = 92.7%，
  `protocol` 0.0% / `closeout` 0.0% → 通过。
- **闸门② GRAD（Qwen3.5-9B，k0–k2）**：本批新题 **50/65 = 76.9%**（7 次上游作废不计分母），
  落在 40–85%；9B 与 27B 都 3/3 的送分题 12/24 = 50% ≤ 70% → 通过。
- **逐题判决**：无返修。没有 REF 3/3 稳定失败的题；9B 失分集中在 `capability` 层（分级正常）。
- **跑分配置偏差（记录在案）**：规格书 §6.2 的 `--chat-api-base` 在 `cmd/rwkv-cli` 里**不存在**
  （实测 `flag provided but not defined`），实际用 `--completion chat-completions --api-url <url>/v1/chat/completions`；
  `--case-timeout` 2m→15m、`--case-parallelism` 40→20（默认 2m 把 5 道需要 4–5 分钟的题判成 infra 失败，
  §12 允许按端点调整并发）。**同一端点同时只跑一个 run**，五批同配置。
- **已发现待主控决定**：(a) log-0007/0008 是 TR-TRUNC、日志 77.9KB/81.5KB，27B 上 3/3 过，
  9B 上 3/3 因超时作废（§10 预告的「27B 会、9B 不会」可测量性边界，未改题）；
  (b) 27B/9B 各有 5 次「答案对但写成一句推导」的 `format` 层失分，属判分口径问题，按 §1.2 记报告不动 scorer；
  (c) **跨批缺陷**：`agent-eval` 的 Go 加载器要求 `expect.run.path` 必须已存在于 `files`，
  而 lint/verify_all 都不查——B3 的 scr-0005/0006/0008 因此让整批加载失败，已在 B3 报告与修复条目中记录。
- 本批题保持 `status: draft`，待全库收口统一置 `reviewed`（见最终条目）。

## 2026-09-22 (扩量 B2 — 新增 24 道 / 6 家族)

- **批次范围**：fam-tab-shipping-04, fam-tab-subscription-05, fam-log-jsonl-04, fam-log-longtail-05, fam-cfg-missing-03, fam-nt-boundary-03。形状固定 L0/L1/L1/L2。
- **自动闸门**：lint 152/0；verify_all 152/152 无 `sabotage_undetected`；web_hitcheck 28 题 5/5；dedup 无近重复对；Go 加载器 152 题全部载入。
- **闸门② GRAD（9B，k=2 轮）**：本批新题 **51/71 = 71.8%**，落在 40–85% 区间。
- **闸门① REF（27B）未完成**：27B 端点 2026-09-22 04:50 起持续 HTTP 502，重跑的 run 无法启动；详见 `reports/expansion-batch-2-2026-09-22.md` 的顶部横幅。

## 2026-09-22 (扩量 B3 — 新增 20 道 / 5 家族)

- **批次范围**：fam-script-report-02, fam-script-fix-03, fam-script-stdlib-04, fam-script-sweep-05, fam-cfg-edit-04。形状固定 L0/L1/L1/L2。
- **自动闸门**：lint 152/0；verify_all 152/152 无 `sabotage_undetected`；web_hitcheck 28 题 5/5；dedup 无近重复对；Go 加载器 152 题全部载入。
- **闸门② GRAD（9B，k=2 轮）**：本批新题 **40/60 = 66.7%**，落在 40–85% 区间。
- **闸门① REF（27B）未完成**：27B 端点 2026-09-22 04:50 起持续 HTTP 502，重跑的 run 无法启动；详见 `reports/expansion-batch-3-2026-09-22.md` 的顶部横幅。

## 2026-09-22 (扩量 B4 — 新增 20 道 / 5 家族)

- **批次范围**：fam-web-deprecation-02, fam-web-errmsg-03, fam-web-version-04, fam-hyb-deps-02, fam-hyb-tax-03。形状固定 L0/L1/L1/L2。
- **自动闸门**：lint 152/0；verify_all 152/152 无 `sabotage_undetected`；web_hitcheck 28 题 5/5；dedup 无近重复对；Go 加载器 152 题全部载入。
- **闸门② GRAD（9B，k=2 轮）**：本批新题 **27/60 = 45.0%**，落在 40–85% 区间。
- **闸门① REF（27B）未完成**：27B 端点 2026-09-22 04:50 起持续 HTTP 502，重跑的 run 无法启动；详见 `reports/expansion-batch-4-2026-09-22.md` 的顶部横幅。

## 2026-09-22 (扩量 B5 — 新增 24 道 / 6 家族)

- **批次范围**：fam-doc-changelog-02, fam-doc-handbook-03, fam-fs-audit-02, fam-fs-dedupe-03, fam-code-testreport-02, fam-code-edge-03。形状固定 L0/L1/L1/L2。
- **自动闸门**：lint 152/0；verify_all 152/152 无 `sabotage_undetected`；web_hitcheck 28 题 5/5；dedup 无近重复对；Go 加载器 152 题全部载入。
- **闸门② GRAD（9B，k=2 轮）**：本批新题 **53/70 = 75.7%**，落在 40–85% 区间。
- **闸门① REF（27B）未完成**：27B 端点 2026-09-22 04:50 起持续 HTTP 502，重跑的 run 无法启动；详见 `reports/expansion-batch-5-2026-09-22.md` 的顶部横幅。

## 2026-09-22 (扩量收口 — 交付状态)

- **题库侧全部完成且全绿**：112 道新题（28 家族 × 4，L0 28 / L1 56 / L2 28），全库 152 题。
  五项题库侧闸门均为全库实测：lint **152/0**、verify_all **152/152**（无 `sabotage_undetected`）、
  web_hitcheck **28/28 题 5/5**、dedup **0 近重复对**、Go 加载器 **152 题全部载入**。
  §8.2 槽位自检逐项吻合：152 / L0 38·L1 76·L2 38 / 38 家族 / 陷阱实例 151 / `traps with <3` 为空 / L3 为空。
- **配置**：`docs/tag-vocab.json` 的 quota 与 level_mix 按 §7.1 改动，`git diff` 恰好 11 行；
  其余跟踪文件（`tools/`、`docs/` 其余部分、现有 40 题）**零改动**。
- **两处返修**（都有硬证据，记在各批报告里）：
  1. **B3**：`agent-eval` 的 Go 加载器要求 `expect.run.path` 必须已在 `files` 里，而 lint/verify_all 都不查，
     导致 scr-0005/0006/0008 让整批加载失败。三题各补一个占位脚本（照 scr-0004 的既有形状）。
  2. **B2**：log-0018 在 27B 上 3/3 因 `HTTP 400 maximum context length is 32768` 作废，
     log-0020 1/3 同因；两题按等比删噪声缩小（60,699→39,921 B / 66,038→44,092 B），
     陷阱几何（唯一 FATAL 的深度、最早 GATEWAY_STALL、注入指令、decoy）逐项保留，`version` → 2。
- **未完成项：闸门①（27B REF）在 B2–B5 上未跑完。** 27B 端点 `http://100.64.0.1:8000/v1`
  自 2026-09-22 04:50 起持续返回 HTTP 502（9B 端点 `:8001` 同期正常）。
  此前该端点已不稳定（`HTTP 502: empty response` / `HTTP 500` / `context deadline exceeded` /
  上下文 400），有两次 run 整批 60 题全挂于 502，这类被污染的 run 已作废重跑。
  重跑所需的 12 个 27B run 已排入队列，端点恢复即自动执行。
  **B1 的闸门① 在同日同配置下已实测通过**（新题 68/72 = 94.4%，protocol 0.0% / closeout 0.0%）。
- **`status` 处置**：**B1 的 24 题置 `reviewed`**（两道闸门均实测通过）；
  **B2–B5 的 88 题保持 `draft`**——§5 规定置 reviewed 的依据是「§6 两道闸门 + 批次报告」，
  闸门①未完成时没有这个依据，不提前置档。
- **`bank_version`**：见 `out/workbank.json`（`tools/build.py --status all`，152 题）。
  `reviewed` 子集当前为 64 题（现有 40 + B1 24）。

## 2026-09-22 (扩量 — 闸门① 补测与定档，bank_version `5e21f039…`)

- **B1 闸门①（27B REF，k0–k2）**：本批新题 68/72 = 94.4%，作废 0，`protocol` 0 / `closeout` 0 → 通过。
- **B2 闸门①（27B REF，k0–k2）**：本批新题 0/0 = n/a，作废 0，`protocol` 0 / `closeout` 0 → 未跑。
- **B3 闸门①（27B REF，k0–k2）**：本批新题 0/0 = n/a，作废 0，`protocol` 0 / `closeout` 0 → 未跑。
- **B4 闸门①（27B REF，k0–k2）**：本批新题 0/0 = n/a，作废 0，`protocol` 0 / `closeout` 0 → 未跑。
- **B5 闸门①（27B REF，k0–k2）**：本批新题 0/0 = n/a，作废 0，`protocol` 0 / `closeout` 0 → 未跑。
- 未全部通过，**只有通过的批次被置 `reviewed`**；未通过或未跑的批次保持 `draft`，不提前定档（§5 要求置档依据是两道闸门 + 批次报告）。
- 详细读数与逐题判决见各批报告；矩阵见 `reports/matrix-5e21f039.md`。

## 2026-09-22 (扩量 — 人工审阅返修，bank_version `f3f189e4…`)

- 输入 `reports/expansion-manual-review-2026-09-22.md`；返修明细与三处判断分歧见 `reports/expansion-review-fixes-2026-09-22.md`。
- **BLOCKER 6 类 8 题全部关闭**：nt-0011/0012 拒绝词表 18→43 条 + `output_excludes` 拦让步型假成功；tab-0008 把站点计酬额移入报表页眉（让 decoy 成为 TR-HEADER 的真实产物）；fs-0008 题面改问字节数以对齐 `expected_number`；cfg-0013 判据换整段 needle 且工单值 1150→960（与 480 同宽，消除注释对齐歧义）；scr-0008 可见导出移入 `sites/`；scr-0007 开关翻成反直觉形态（裸跑=净额，`--gross`=今天的毛额，`expect.run.args` → `[]`）。
- **B-2 未按报告的两个选项办**：`TR-HEADER` 全库仅 3 实例，改挂陷阱会破坏「每陷阱 ≥3」；加陷阱又会把 tab-0006 顶到 L2、tab-0008 顶到 L3（L3 须为空）。tab-0006 的 1840.0 天然有两条收敛路径（抄 TOTAL 行 / 不按部门汇总），无 fixture 改动可分开，改为在 NOTES 写明归因告诫（3680.0 才是合计行独有产物）。
- **B-4 未用 `equals`**：逐字节比较会把「write_file 少写结尾换行」判成失败（判 harness 不判模型）。改用整段多行 needle，cfg-0014/0015/0016 同手法加固。
- **裁决 3 项**：web-0005 摘要补上版本号、题面 removal→deprecation；web-0006 两条结果摘要各带自己的说法（3.9.0/4.2.0），冲突上浮到结果层由 `published_at` 判新旧；nt-0010/hyb-0011 的 turn-1 词表收紧为只保留「在问」的标记（删 `let me know`/`period`/`quarter`）；scr-0019 的两条判不到的承诺记入该题 Grading note。
- **S-A 21 处 NOTES/文档数字失实全部订正**，每条以 python 从 fixture 实算复核；其中 **2 条与审阅报告的说法不同，以实算为准**：tab-0020 月先读实际翻转 4 行（报告称 2 行），scr-0011 的 decoy 应取判分期（hidden 已写入，STR-6602 会出现，total 336445）而非可见三份的汇总。
- **S-B 判据宽容度**：web-0009..0012 补大小写形；nt-0007 兼收 `git annotate`；code-0007/0008 改 `output_contains_any`（未采用双 token——schema 表达不了 AND-of-OR，且 `completed` 是题面自带的免费 token）；web-0014/0016 用 `output_equals_any` 容下出处形——**没有**改成 `output_contains`，因为 `verify_all` 只收集 equals 家族，改了就会让这两题（无 files、sabotage 跳过）失去唯一的自动互证。
- **另修三条公平性问题**（在逐题表里、不在 §7 清单上）：log-0006 的 `billing-ops.md` "one line means one request" 正面为 decoy 背书，改为「从不把同一行写两次」；hyb-0006 的 `expect.tools: []` 零调用契约与 3 步参考解矛盾，改 `forbidden_tools: [web_search, web_fetch]`（`max_calls: 0` 会被加载器判非法）；hyb-0011 的 README "usually opened against the most recent billing period" 让不反问直答变得有据可依，删。
- **闸门**：lint 152/0、test_lint 8/8、verify_all 152/152（warning 分布与返修前逐题一致）、dedup 0 对、coverage 无缺口、web_hitcheck 16/16；既有 40 题 `git diff` 仍为空。
- **status 不动**（88 draft / 64 reviewed）：置档依据是两道闸门 + 批次报告，闸门① 在 B2–B5 未跑完，且本轮返修发生在 B1 那次闸门**之后**。**B1 已 reviewed 的 4 题被改动**：tab-0008、log-0006 改了 fixture（读数需重测），nt-0007 仅放宽判据（旧通过仍通过），tab-0006 仅 NOTES（不影响，version 保持 1）。
- **移交工具轮**：`FileExpectation` 缺 `excludes`；`verify_all` 只收集三种 expect 形状（43 题互证空转）；`RunExpectation` 单次调用 + 判分副本用后即删（scr-0019 两条承诺、scr-0007 的 `--gross` 分支判不到）。

## 2026-09-22 (9B 跑分 + 下架 4 题，bank_version `401b863f…`)

- **9B 全库跑分**（`qwen3.5-9b` @ `100.64.0.1:8001`，152 题 × k0/k1/k2，`--case-parallelism 40`，其余参数同批次报告；27B 本轮不跑）：
  官方通过 **300/450 = 66.7%**（单轮 66.0/65.8/65.0，极差 1.0pp），作废 6，
  分层 `infra` 6 · `closeout` 5 · `format` 17 · `capability` 128，
  `protocol` 0.0% / `closeout` 1.1% → **可以当能力读数**。
  3/3 通过 75 题、3/3 稳定失败 28 题、抖动 45 题。产物：`runs/workbank/postfix-152-grad-k{0,1,2}`。
- **web 场景的失败主因是不调网络工具，不是答错**：16 题 × 3 轮 = 48 次作答中只有 21 次调了 `web_search`；
  **调了的过 17/21 = 81%，没调的过 0/27 = 0%**。没调的那些是在空工作区里 `search_text` + `list_files`
  翻七八步后回 UNKNOWN。冻结的 web-0001/0002 同样挂法 → 是 9B 的固有工具选择行为，与本轮返修无关。
- **下架 4 题**（移入 `cases-shelved/`，题目文件未改动，移回即恢复）：
  `log-0007`（单文件 77,867 B）、`log-0008`（81,541 B）、`log-0020`（44,092 B）、
  `fs-0006`（831 个文件，最大单文件仅 456 B——撑爆的是目录列表）。
  三轮里它们各有 1–2 次被上游 `HTTP 400: maximum context length is 32768` 判为 `invalid`，
  **而 invalid 会被踢出分母**：模型选错取数方式不失分，只是让这道题从测量里消失。
  判据是目标模型 RWKV 只有 16k 上下文（实际可用更少），16k 下连正确路径也会炸。
  对照证据：**log-0008（全库最大）在模型走 `search_text` + `read_lines` 的那轮完整跑完并被正常判错**
  ——设计意图（grep 式取数而非整文件读入）是通的，`search_text` 就是 grep 的位置，并不缺 bash。
- **保留 `doc-0012`（47,844 B）与 `log-0018`（39,921 B）**：两道 3/3 全过、从未作废，按 16k 口径同样超预算，
  但目前测得动；等真在 RWKV 上跑过再按实测决定缩题还是下架。
- **配额缺口有意留着**（未改 tag-vocab.json）：`logs` 20→17、`filesystem` 12→11、全库 152→**148**；
  `coverage.py` 报 `logs L2: need 5, have 3`。陷阱普查仍全部 ≥3，但
  **TR-TRUNC 6→3、TR-LONG 4→3、TR-INJECT 4→3 已卡在下限**，再下架带这三个陷阱的题即跌破。
- **闸门（148 题）**：lint 148/0、test_lint 8/8、verify_all 148/148、dedup 0 对。
- 未决：`code-0008` 判据仍偏窄（模型答 "without any check" / "doesn't implement" 这类正确措辞未命中），待修。

## 2026-09-22 (deepseek-flash 摸底 + web 题检索契约，bank_version `11a561f5…`)

- **温度是决定性配置，本模型不能用 greedy。** 先按本地 9B/27B 的参数用 `--temperature 0` 跑，
  148 题只有 109/148 = 73.6%，伴随大量「UNKNOWN 早退」（18 题）与「不调 web_search」（12/16）；
  换 `--temperature 0.3` 后同一套系统提示词、同一模型、同一批题拿到 **279/294 = 94.9%**
  （k0 139/146、k1 140/148），UNKNOWN 早退降到 1–2 题、web 检索率升到 15–16/16，
  冻结 40 题回到 **39/40 与 38/40**，与 2026-09-21 `flash-*` 系列吻合。
  2026-09-21 的 sweep 早已测出同一结论（`runs/workbank/flash-greedy-k*` 五轮作废 14→28→31→33→40）。
  **教训记在 reports/dsflash-baseline-2026-09-22.md §2**：给没跑过的端点定参数前先翻 `runs/`；
  本轮因此在坏配置上做了一整轮「系统提示词压制检索」的分析，结论全部作废——那些现象是温度 0 的伪影。
  相应地，系统提示词的两处实验（加「别放弃」一句、去掉 `local-first`）**不落库**。
- **16 道 web 题加 `expect.required_tools: ["web_search"]`**：这些题没有工作区文件、题面也不含 URL，
  不检索不可能答出来。它不改变通过与否，改的是归因——失败信息变成
  `required tool "web_search" was not called`，不再把「模型没出门」记成能力问题。
- **16 道 web 题面补一句「本地没有」的上下文**：工作区是空的而系统提示词第一句是
  `You are a local-first assistant`，模型看到空目录后按 UNKNOWN 契约退出。补的是真实用户会说的话，
  不是工具暗示（题面出现工具名会被 lint 拦下）。T=0.3 下检索率本就 15–16/16，
  **这句话没有可证明的收益**，保留的理由是题面对齐用户环境（主控口径）。各题 version+1。
- **`tools/capability_gate.py` 新增 `toolchoice` 层**（v1→v2）：把「没调必需工具」从 `capability` 层分出来。
  T=0.3 下只剩 1 例，说明「没出门」本就罕见，这条现在是便宜的保险。
- **13 道失败逐题见报告 §3**：真正像「模型不会」的只有 code-0002、hyb-0002 两道，且都是 1 过 1 挂的抖动。
  其余是判据/预算问题 4 道（web-0002 的 `output_equals` 拒了带出处的正确答案——S-B 漏网；
  web-0014 答对却撞 `max_calls: {web_search: 1}`；code-0008 词表仍未覆盖 "claims" 类说法）、
  script 家族步数耗尽 3 道（`forced_answers: 1`，脚本没写完或没写成，却被记进 `capability` 层）、
  上游 tool_call 参数非 JSON 2 道、输出 token 上限 2 道。**本轮按主控决定不修，列入待办。**
- **闸门（148 题）**：lint 148/0、test_lint 8/8、verify_all 148/148、dedup 0 对、web_hitcheck 16/16。
- 待办：web-0002 / code-0008 判据；web-0014 的检索预算；script 步数预算与 `forced_answers` 的分层归因；
  **9B 三轮与扩量轮 B1–B5 的闸门读数全是 T=0 下测的，可能严重低估，值得按 T=0.3 重测**。
