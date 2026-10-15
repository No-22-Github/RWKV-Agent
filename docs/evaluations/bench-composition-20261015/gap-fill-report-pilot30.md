# GPT 6 luna 补题试点：30 题审查报告

## 结论

**暂不扩大，也不并入正式考卷。** GPT 6 luna 能完成题面、fixture 和大部分参考计算，但首稿及按反馈修订的版本仍反复出现“判分与真实目标不一致”的问题。本轮不是未经干预的 luna 原始能力测量：主 Agent 逐题审查、退回多次，并直接修过部分内容。即便如此，当前仍有 **7 题需要重新设计判分，5 题受 verify 破坏探针边界阻塞**；其余 18 题仅保留为草稿候选，未冒充人工批准。

全部 30 道候选保存在 **`bench/exam/pilots/luna-20261015/cases/<scenario>/<id>/`**，共 90 个附件文件。未放进自动导入的 `bench/exam/cases/`，避免未验收题自动进入考卷。全体 `status=draft`、`author=llm:gpt-6-luna`、`reviewer=null`。逐题可读结论见下面清单及各题 NOTES；机器清单和 case.json SHA-256 见同目录 `gap-fill-pilot30-review.json`。

## 范围、编号和出题过程

- 用户 2026-10-15 授权改号段，并将试点由 6 题改为 30 题；不合格时先汇报，交由用户决定下一步。
- 规格 M0 的 6xxx 已被 `bench/distill/v1/cases/` 的 150 题占用；全仓检查 11000–11999 未占用，bank lint 解析式接受 4–5 位数字，因此采用 `<abbrev>-11001` 起的编号。未改解析器或词表。
- 三个 `gpt-6-luna` 子 Agent 各起草 10 题；主 Agent 审查全部题面、答案、oracle、约束和盲解结果。不是只抽查失败题。
- G1 24 道完整覆盖：配置 5（L0×2/L1×3）、统计写产物 6（L1×4/L2×2）、文档结构化 5（L1×5）、批量编辑/删除 4（L1×3/L2×1，含 2 道删除）、脚本修复 4（L1×2/L2×2）。G2 先试 6 道：直接计算 3、歧义反问 2、能力边界 1。全为中文。未启动 G3–G6，也未补完 G2 剩余 10 题。
- 与原规格逐批验收的差异：用户要求 30 题试点，本次同时取 G1 全批 + G2 一部分；不表示两个批次已正式验收。

## 主审发现及处理

| 问题 | 例子 | 处理与当前状态 |
|---|---|---|
| 题面与答案范围不同 | tab-11003 要各工位，原 oracle 只算校准台，且输出路径不同 | 已修为全部工位：封装 9.25、校准 8.00、光学 7.25，并核对排序和路径 |
| 自由排版却全文相等 | doc-11002..05 锁未指定标题、空格和措辞 | 改钉完整关键事实后真实正确产物可过，但反例表明仍会漏判结构和额外错误，4 题暂不收录 |
| 反问锁完整话术 | nt-11005/06 只认四句完整回答，甚至引用未读配置值 | 不给老师本次回答加白名单；两题退回重设计。语义正确的独立反问也能复现误判 |
| 配置合并的末尾换行 | cfg-11005 在主审将判分收紧为全文 equals 后，合法追加配置但无最终 LF 被判错 | 这是本轮含主审修改版本暴露的问题，不全归因于 luna。仍需重设计，不能改成短子串并放过 `/healthzz` 或重复键覆盖 |
| 日期只改了一部分 | fs-11002 题面改为 09-12，fixture 路径和 expect 仍是 09-18 | 同步所有 JSON 键、内容、oracle、题面；单题复测通过 |
| 文件检查互斥字段混用 | fs-11001 同一路径 unchanged + contains；Agent 声称修好后仍残留两处 | 首次 loader 拒绝整套，尚未调用模型；主审统一改为 equals。bank lint/verify 没拦住此问题 |
| 未保护输入资料 | 多道产物/脚本题只判输出，改坏源数据也可能过 | 加入非目标 fixture 保持原样检查；脚本按运行 stdout 判分，不锁源码写法 |
| 标签或资料细节不实 | decoy 写成正确值 + 1、缺值只有两种、美元却按元记、重复 canary、NOTES 错误数值 | 已修；L1 题删除无关装饰 fixture，规则保留在 fixture，不把陷阱做法写入题面 |

文件 contains 的漏判有实际反例，不只是推测：把 doc-11003 钉住的问答全放进去，再附加“现行寄送地点：杭州旧站点”，规则仍通过；doc-11004 同理可以附加错误的“离线草稿本次已发布”。doc-11002/05 即使只是未编号、未成表的词句堆叠也能通过。原生规则只有 equals/contains/absent/unchanged，当前做法无法同时宽容合法排版并验证这些语义。原始反例在 `local/runs/exam-gapfill-20261015/file-false-positive-review.json`。

## DeepSeek 盲解与逐题失败归因

配置：App harness、work-v2、暂存文件；`deepseek-flash`、native Chat Completions、上游思考 disabled、T=0.3、top_p=1、并发 12，默认预算 16 步 / 4096 最终回答 / 2048 决策 / 1800 秒。按需求单只做单次 k0 题目验收，不是模型排名实验。

实际首次启动因 fs-11001 互斥字段被 loader 拒绝，未产生有效盲解结果；修复后完整盲解为 **23/30（76.7%），invalid=0**，低于 85%。`run check --arm t03-p10 --cases 30` 全通过。完整跑用的 case 副本在 `local/runs/exam-gapfill-20261015/loader-fixed30-cases/`，结果在 `pilot30-deepseek-k0/`；更早失败源快照为 `first30-cases/`。

| ID | 归类 | 证据与处理 |
|---|---|---|
| cfg-11005 | 题有问题：不公平格式要求 | 配置值、保留值、追加位置都正确，仅新行无最终 LF；仍退回，不缩短匹配蒙混过关 |
| fs-11002 | 题有问题：题面/fixture 不一致 | 用户指 09-12，实际只有 09-18；老师合理地拒删。已修，独立 `fs-11002-repaired-k0` **1/1 通过**，单题闸门也通过 |
| nt-11001 | 老师选工具失败 | 数字 8300 正确，但调用 calculator，违反 tools=[] / active no-call；保留判分，NOTES 写 Teacher result |
| nt-11005 | 题有问题，且老师也违反 no-call | 老师反问了环境与天数，但不能命中作者完整话术；同时确实读了文件，不应因此改判为通过。退回重设计 |
| nt-11006 | 题有问题，且老师也违反 no-call | 同义澄清不匹配；当前回答使用英文，但题目未禁止英文，不能据此扣分。老师另外读了配置，no-call 失败成立。退回重设计 |
| scr-11004 | 老师漏输出零值项 | 每个站点应包含南站 0，修后脚本只输出有告警站点；保留 stdout 判分，NOTES 写 Teacher result |
| tab-11005 | 老师实际文件排序错误 | 文件把 980.75 放在 1195.75 前；答复虽口头纠正顺序，未修文件。保留判分，NOTES 写 Teacher result |

以上不合并成一份“修后 24/30”成绩：30 题结果和 1 题复测是两份原生 run，未手拼 summary。完整盲解只有 23/30 这一份结果。23 道通过题的实际编辑/答案也已检查；未观察到该次正确率内的实际错答，但定向反例证明 4 道文档题的判分存在漏判。

## 本地检查、去污染及合入状态

- HEAD：`537d598598d8e446e69ec3ee965590c6a0759d23`；开工工作区干净。rwkv-cli、rwkv-lab、chatcompletions 版 rwkv-cli-chat 均本次从源码重编。加题后的盲解含未提交候选，按规程记为探索验收。配置模型可在 `/models` 找到；未将别名当作服务端底层版本证明。
- 最终 `bank lint --cases bench/exam/pilots/luna-20261015/cases --canary-prefix EXAM-CANARY`：**30 checked，0 violation**。
- 最终 `bank verify --strict-shape`：**25 passed，5 failed**。五道均通过答案比对，仅 sabotage 未检出：nt-11001..03 的答案来自用户消息，改坏旧文件理应不变；tab-11001/05 被删除的是不影响聚合的报表标题。没有加入无关断言去伪过。
- 主审另做语义变异：修改三道题面数值，分别得到 8301、818、8280；修改两道表的有效金额，结果也相应变化；改旧文件/删标题则结果保持不变。10 项这类检查均通过。两个正常反问反例被作者规则拒绝，另记录为 2 项失败。证据：`local/runs/exam-gapfill-20261015/semantic-review.json`。这不能替代强制 M1 全通过，检查器问题留给维护者。
- 负向测试：隔离副本中把 nt-11001 expected_number 改错 123，verify 在 expect_match 阶段报 FAIL、退出 1；未污染正式候选。证据 `negative-number.json`。
- 最终结构复查：30 题 / 90 文件 / 30 个唯一 canary，description 后缀、verify 首行、NOTES 末行一致；路径、fixture_bytes、作者、draft 和文件检查互斥项均核对。
- 去污染默认阈值未调整：v1（759候选）0 flagged；v1.3（782）0；v1.4（1012）**1 flagged**；v1.41（430）0；v2.0（940）0；v1.42/cases 本地不存在，记未执行。剩余命中为训练 web-8061 与需重设计的 nt-11006，只有 names 相似度 0.33，prompt/files 都为 0；不能据此证明污染，也不能声称 M3 全通过。日志 `decontam-final-v*.txt`。早期 todo/FAQ 名称还产生过纯标识命中，已改为业务中文产物路径，未改训练数据。
- **M4 不执行合入/build 或 stale 负向测试**：试点尚未验收，保存在隔离目录。现有正式考卷仍为 378 题，`exam lint` 为 0 violation，`go test ./internal/lab/exam/` 通过；未改生成清单、旧题、quick 选择或 internal/cmd。没有新发现并修旧题；本轮列出的 loader/lint、破坏探针、smalltalk 冲突均只记录。
- smalltalk 的独立冲突：需求单说不锁关键词，bank lint 却要求非空 output_contains_any，因此本次不拿闲聊凑数。
- **没有 git commit 或 push**。

## 逐题清单

“可保留的草稿候选”不等于人工审核通过；“verify 阻塞”表示内容经独立变异复核，但强制命令仍失败；“需重新设计”不应直接挪进自动导入目录。

| ID | task_type | 难度 | 主审结论 |
|---|---|---|---|
| cfg-11001 | edit_value | L0 | 可保留的草稿候选 |
| cfg-11002 | edit_value | L0 | 可保留的草稿候选 |
| cfg-11003 | edit_value | L1 | 可保留的草稿候选 |
| cfg-11004 | edit_value | L1 | 可保留的草稿候选 |
| cfg-11005 | merge | L1 | 需重新设计判分 |
| doc-11001 | write_structured | L1 | 可保留的草稿候选 |
| doc-11002 | write_structured | L1 | 需重新设计判分 |
| doc-11003 | write_structured | L1 | 需重新设计判分 |
| doc-11004 | write_structured | L1 | 需重新设计判分 |
| doc-11005 | write_structured | L1 | 需重新设计判分 |
| fs-11001 | bulk_edit | L1 | 可保留的草稿候选 |
| fs-11002 | scoped_delete | L1 | 可保留的草稿候选 |
| fs-11003 | bulk_edit | L1 | 可保留的草稿候选 |
| fs-11004 | scoped_delete | L2 | 可保留的草稿候选 |
| nt-11001 | snippet_in_reply | L1 | 内容可保留，但 verify 破坏探针阻塞 |
| nt-11002 | snippet_in_reply | L1 | 内容可保留，但 verify 破坏探针阻塞 |
| nt-11003 | unit_convert | L1 | 内容可保留，但 verify 破坏探针阻塞 |
| nt-11004 | beyond_capability | L1 | 可保留的草稿候选 |
| nt-11005 | ambiguous_request | L1 | 需重新设计判分 |
| nt-11006 | ambiguous_request | L1 | 需重新设计判分 |
| scr-11001 | fix_output | L1 | 可保留的草稿候选 |
| scr-11002 | fix_output | L1 | 可保留的草稿候选 |
| scr-11003 | fix_output | L2 | 可保留的草稿候选 |
| scr-11004 | fix_from_traceback | L2 | 可保留的草稿候选 |
| tab-11001 | write_summary | L1 | 内容可保留，但 verify 破坏探针阻塞 |
| tab-11002 | write_summary | L1 | 可保留的草稿候选 |
| tab-11003 | write_summary | L1 | 可保留的草稿候选 |
| tab-11004 | write_summary | L1 | 可保留的草稿候选 |
| tab-11005 | write_summary | L2 | 内容可保留，但 verify 破坏探针阻塞 |
| tab-11006 | write_summary | L2 | 可保留的草稿候选 |

## 后续建议

先由更强的模型或维护者定好少量可复用的判分模板、解决上述检查器边界，再让 luna 填数据与起草；每批继续主审。当前不适合让 luna 独立批量产题后仅凭 lint/verify 自动收录。是否接受这种分工、改换出题模型或先补判分能力，留给用户决定。
