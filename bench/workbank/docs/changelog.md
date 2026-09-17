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
