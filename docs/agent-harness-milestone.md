# RWKV-Agent 只读 Agent Harness 里程碑

状态：Phase 1 部分完成

目标：在现有 macOS 本地推理、Conversation 和 State 能力之上，建立可测试、可约束的
Agent step loop；先证明模型能可靠地依据仓库证据回答，再逐步开放有副作用的能力。

## 1. 路线选择

现有推理 CLI、Session 持久化、连续批处理、TUI 和 PTH 直载已经完成真实模型验收。下一个
产品缺口不是新的推理 Demo，而是仓库名称中的 Agent Harness。

第一阶段选择只读仓库 Agent：

1. 第一轮允许普通文本直接回答；只有以 `<tool_call>` 开头的输出进入严格控制帧解析。
2. 工具选择阶段采用 greedy 解码和严格 envelope/JSON 解析。
3. `inspect` 路由的第一次工具选择预填 `<tool_call>`；模型只生成受约束的 JSON 尾部。
4. 工具尝试后允许继续调用另一个不同工具或直接回答；最后一个 step 和重复调用会触发
   禁用工具、预填 `<answer>` 的独立回答阶段，文件内容始终视为不可信数据。
5. 失败调用提供确定性恢复提示；同一工具连续执行失败两次后阻断第三次调用。
6. 限制总 step 和协议重试次数，避免无界循环。
7. 只开放只读工作区工具、确定性计算工具和固定 mock 助手 Provider。
8. 暂不开放写文件、shell、Git、网络和动态插件。

## 2. 已落地

- `rwkv-cli agent --model ... --workspace ... --prompt ...` 一次性任务入口。
- `rwkv-cli agent --model ... --workspace ...` 多轮 TUI 入口；交互终端自动选择，
  非交互环境保持 plain 输出。
- Runner 事务化保存进程内 user/assistant/tool transcript；后续轮次的工具选择和独立
  最终回答阶段都携带已提交历史。
- 取消、生成失败、协议错误和 step 超限不提交当前轮；`/new`、`/reset` 显式清空历史。
- Agent TUI 展示 Conversation、step、工具活动、只读权限和工作区，支持当前轮取消后继续。
- 每轮由模型驱动的 `respond|inspect` Router 先判断是否需要新工作区证据；Router 不接收
  工具 schema 或原始 tool payload，Harness 只解析路由结果，不使用关键词意图启发式。
- `respond` 路由不开放工具；Router 协议重试后仍失败则 fail closed 到 `respond`。
- `inspect` 路由首次工具动作预填 `<tool_call>`，Runner 重建完整 frame 后严格解析。
- `tool` / `final` 两类 G1I envelope 动作及严格字段校验。
- 普通文本 final 与 G1I 工具控制帧的联合输出语义。
- 一次协议纠错重试和 2–20 step 硬上限；至少两步才能在工具后保留最终回答。
- 工作区相对路径、`..`、绝对路径和符号链接越界检查。
- 64 KiB 单文件上限、2 MiB 搜索文件上限和结果数量上限。
- 连续不同工具调用、成功或失败的精确重复调用拒绝、完整工具轨迹和独立最终回答阶段的
  消息闭环。
- 同一工具连续失败最多实际执行两次，`read_file` 缺失路径提供 discovery 工具提示。
- 参数校验失败提供工具的精确参数形状；修复调用不消耗运行时连续失败预算。
- `inspect` 轮没有任何可信工具观察时以 `ErrNoWorkspaceEvidence` 失败并回滚，不生成或提交
  无证据答案。
- 任意工具尝试后预留最终回答 step；证据不足时收束为明确限制，而不是以 step 超限结束。
- 模型无关的 completion 注入；控制提示支持标准 system 与 G1 inline 两种装配模式。
- 独立的 `continuation.Generator`、`ActionProtocol` 和 `PromptRenderer` 接口。
- 本地 inference Session 续写 adapter。
- `rwkv_lightning` 非流式 HTTP 续写 adapter；endpoint 可配置，密码来自环境变量。
- `rwkv-g1i-envelope-v1` 与 `rwkv-chat-continuation-v1` 独立版本标识。
- 协议、循环、路径越界、截断、搜索与读取的无模型单元测试。
- 回答阶段对长字符串保留开头和任务相关窗口，单个字符串约束为 2400 Unicode 字符。
- `rwkv-cli agent-eval` 可运行内置或 `schema_version: 3` 的自定义 case；每个 case
  隔离临时工作区，本地模式使用独立 inference Session，同一 case 内保留多轮状态。
- 评测原子写入 `run.json`、`trace.jsonl` 和 `summary.json`；记录模型/协议/采样版本、
  原始 continuation、Runner/tool 事件和分项指标，失败 case 也保留诊断产物。
- 内置 suite 拆成 10-case `smoke` 和默认 18-case `boundary`；后者改造自
  `marty1885/primitive-bench@e0af1723` 的只读任务，并记录分类、来源和难度。
- 边界判分支持无序必需工具、禁止工具、参数子集调用、严格答案和数值容差；保留 smoke
  的精确有序工具/调用判分。
- P0 助手工具包括 `weather`、`nearest_transit`、`transit_hours`、`fx_convert`、
  `calculator`、`structured_query` 和 `datetime`；外部事实使用固定 mock Provider，
  `structured_query` 复用统一工作区越界策略。
- Provider 不可用会进入不可重试的显式降级路径，最终回答 prompt 注入未验证事实清单。
- `rwkv-agent-eval-v8` 增加独立 6-case `assistant` suite、plan 预留指标、显式弃答指标，
  boundary 同时注册 `calculator` 与 `structured_query`，但仍与 assistant 分轨计分。
- 最终答案提交前拒绝协议标签、role header、整段 JSON 和原始工具 payload；用户看到并写入
  transcript 的是确定性弃答，模型原文仍保留给 `answer_accuracy`，修复发生率单独统计。

2026-07-30 的 `rwkv-g1i-13b-4922` 远程 smoke test 覆盖直接回答、`read_file` 和
`search_text`，三条均完成且未触发协议重试。旧裸 JSON 协议已经删除。协议结构参考
`123123213weqw/rwkv-agent`；完整能力评测计划复用 `marty1885/primitive-bench`。
“你有哪些工具”和包含协议标签的文档总结也已回归通过。

同日首轮 `agent-eval` 内置 suite 结果为 10/10：11/11 route、19/19 协议动作、
8/8 工具参数和 3/3 no-call 均正确，没有协议重试或 Router fallback。30 次远程模型调用
总耗时 40.4 秒；服务端 usage 字段仍为 0，因此本轮不能评价 token 效率。

同日 `boundary` 首轮结果为 4/18：答案 6/18，route 18/18，协议动作 43/43，必需工具
15/22，禁止工具 2/2，必需调用 15/23，61 次模型请求总耗时 91.2 秒。失败可分为：

- 发现后读取、两文件比较等 5 题命中当前“一次成功工具调用后立即回答”的 Runner 边界。
- 日志、配置和源码探索 3 题出现错误路径、错误工具或没有读取证据。
- 财务计算、JSONL 聚合、退款对账和严格 flag 输出等 6 题答案错误。

这说明原 10/10 只覆盖 smoke contract，不能代表 13B Agent 能力。

放开连续成功工具调用后的第二轮 `boundary` 对照为 10/18：答案 10/18，必需工具 20/22，
必需调用 21/23，route 和协议动作仍为 100%。它修复了发现后读取、搜索后读取、多文件
比较、缺失文件恢复、长上下文定位和 release notes 等任务，但工具调用从 26 增至 65，
错误从 9 增至 32；CSV、财务和 JSONL 等 8 题因模型继续调用直到 step 上限而没有答案。

当前 `rwkv-agent-eval-v4` 因此改为混合状态机：成功后继续开放不同工具并给出收束提醒，
重复成功调用不会再次执行且会触发强制回答；若已有成功结果，最后一个 step 固定使用全部
累计工具轨迹回答。同套 18 题实测仍为 10/18，必需工具和调用保持 20/22、21/23；工具
调用由自由循环的 65 降至 54，错误由 32 降至 23，原先 8 个无回答失败降至 1 个。
`pb_csv_sum` 恢复通过，但 `pb_markdown_release_notes` 找到正确 flag 后附带解释，未通过
严格字符串判分。这说明 v4 改善了有界收束和失败可诊断性，但没有提高本轮总分。

`rwkv-agent-eval-v5` 进一步加入首次工具 frame 预填、失败恢复和强制收束，并新增
工具实际执行、Controller 拒绝、重复调用、连续失败阻断与强制回答指标。同一 13B
`boundary` suite 复测仍为 10/18，8 个失败 case 集合未变；答案分项由 10/18 升至 11/18，
必需工具和调用分别升至 21/22、22/23，工具请求由 54 降至 50、错误由 23 降至 15，唯一
的 step 超限空答案降至 0。38 次实际执行之外有 12 次重复调用被拒绝，14 个 turn 进入
强制回答，连续失败阻断没有触发。结论是 v5 改善了收束和调用效率，但没有提高任务通过率。

v5 `smoke` 严格工具序列评分为 4/10，但 11/11 回答、route 和协议动作均正确；6 个失败
来自证据充分后的额外工具调用。早期 10/10 smoke 使用“一次成功工具后立即回答”的状态机，
不适合作为当前多工具循环的直接发布门槛。

`rwkv-agent-eval-v6` 在 v5 上增加参数 schema 定向修复和无可信工作区证据时的事务回滚。

`rwkv-agent-eval-v7` 增加默认关闭的 `--few-shot` profile，用完整对话轨迹演示成功后停止、
证据不足时继续、参数修复和严格输出格式。同一 13B 的 A/B 中，smoke 从 4/10 升至 5/10，
工具请求由 21 降至 16；boundary 却从 10/18 降至 7/18，答案由 11/18 降至 8/18。
失败轨迹出现对示例路径 `notes/title.txt` 和示例值 `EMBER-7` 的直接复制。结论是静态完整
few-shot 能改善局部停止效率，但对当前模型有严重锚定副作用，不能设为默认策略。

2026-08-04 的 P0 无模型验收用脚本 continuation 完整跑通问题 A、问题 B 和汇率不可用变体，
三题均通过，证明 Router/Runner、mock 工具、Provider 降级和评测判分链路闭环。该结果只代表
Harness 验收，不代表 `rwkv-g1i-13b-4922` 能力。

同日使用 `rwkv-g1i-13b-4922` 完成真实远程验收，原始产物分别位于
`runs/api-13b-v8-assistant-20260804-01/` 和
`runs/api-13b-v8-boundary-compute-20260804-01/`。`assistant` 原始任务通过 1/6、回答 1/6、
route 5/6、协议 23/23、精确工具序列 1/5、参数 2/8；没有触发协议重试、Router fallback
或答案契约修复。逐题结果如下：

| case | 实际结果 | 主要归因 |
|---|---|---|
| `as_weather_transit_hours` | `weather -> transit_hours("上海")`，缺少 `nearest_transit` | 模型依赖分解和参数传递失败 |
| `as_expense_fx_convert` | 额外读取文件，错误过滤后只汇总 100 CNY，换算 14 USD | 模型工具选择和过滤参数失败；工具错误反馈正常 |
| `as_expense_fx_unavailable` | 本地总额误报 0，但明确说明 FX Provider 不可用 | 模型生成不支持的过滤语法；旧解析器又静默返回 0；`未完成` 字面判分是假阴性 |
| `as_single_weather` | 单次 `weather` 后正确回答 | 通过 |
| `as_two_independent_facts` | 两个工具和事实均正确，日期写成 `2026年8月4日` | 语义通过；要求字面 `2026-08-04` 的判分过严 |
| `as_ambiguous_needs_clarify` | 擅自猜北京并重复调用天气 | 模型未澄清歧义 |

因此原始分是 1/6；剔除日期格式假阴性后，语义任务完成约为 2/6。汇率不可用题虽然正确
拒绝猜测，但本地总额仍错误，不能整体改判为通过。模型已经能稳定地产生合法控制帧和完成
单工具事实题，但多步规划、参数生成、证据充分性判断与歧义处理仍明显不足。

本轮远程产物生成后，`structured_query` 已改为拒绝 `>=`、`<=`、`!=`、`==` 等不支持的
过滤表达式，并在工具说明中明确只接受空过滤、`本周`/`this week` 或精确 `field=value`；
assistant 判分也已接受 ISO/中文日期二选一和“不可用”降级措辞。修复后的远程分数尚未复测，
因此上面的原始分保持不变，不用离线重算冒充新模型结果。

A4 `boundary` 复测为任务 8/18、回答 10/18、route 18/18、协议 77/77、必需工具 19/22、
必需调用 20/23；60 次工具请求中实际执行 47 次，22 次报错，13 次重复调用被拒绝，16 题
进入强制回答。指定的 5 个算术/聚合失败全部仍失败（0/5）：利息只算一段、EUR 对比拆解
错误、汇率列选择错误、JSONL 请求了不支持的复合聚合、CSV 对账只输出 SKU。`calculator`
执行本身是确定性的，失败主要在模型没有把任务拆成正确表达式；现有 `structured_query` 也只
支持单一 `sum|count|avg` 和精确过滤，不能直接表达多指标、分组、列选择或跨表计算。

结论：P0 代码和无模型闭环已落地，但 A4 的 `>=3/5` 硬门槛未达到，P0 不算完成，暂不进入
P1 或开放有副作用工具。Harness 继续只负责协议、权限、预算、执行、重复拒绝和提交策略；
不增加题目关键词路由或任务特判来掩盖模型能力。

## 3. 当前边界

- Agent transcript 已支持进程内多轮提交和重置，但尚未接入不可变 Session bundle，
  进程退出后不能续跑。
- 尚无全局 token 预算；当前只有回答阶段的单字符串字符预算。
- 工具动作有严格结构解析，最终答案有结构泄漏校验；正文语义和格式遵循仍由模型负责。
- 已有英文边界任务和错误工具参数/多步查找的三轮 13B 数据，但尚缺中文边界题、重复运行
  稳定性和 7B/3B 横向比较。
- 当前 1.5B G1 的协议遵循不足，不能把 CLI 入口视为可用 Agent 产品。
- 任务相关性压缩是轻量词项窗口选择，尚未做 tokenizer 级预算或语义重排。
- 不支持并行工具调用。
- 已支持顺序多工具调用，但没有显式 planner、依赖图或动态 step/token 预算。
- `rwkv_lightning` 当前只返回通用 `finish_reason=stop`，预算耗尽与命中 stop string
  无法可靠区分；CLI 暂以 96 token 限制首次工具选择，以 1024 token 默认回答预算降低
  语义截断概率。
- 远程续写第一版还没有 SSE 流式输出、usage 统计或服务端 State 对接。
- 已有 10-case smoke、18-case boundary、无模型回归测试和三轮真实 13B 边界结果，但
  尚未验证重复运行稳定性，也尚未定义用于 CI/发布的最低通过门槛。

## 4. 下一步 Checklist

### Commit A：Agent Session 持久化

- transcript 保存 system/user/assistant/tool 的完整结构化消息。
- Agent revision 绑定工具注册表版本与工作区标识。
- 中断后只恢复已完成 step，不保存半个模型动作或半个工具结果。
- native State 不可用时从 transcript replay。

### Commit B：上下文预算

- 每步生成前统计 prompt token。
- 工具结果按字节和 token 双重限制。
- 超预算时先丢弃可重新获取的旧工具正文，保留路径、摘要和 checksum。
- 明确报告压缩次数、压缩前后 token 和是否触发 replay。

### Commit C：权限契约

- 为 ToolSpec 增加只读、写入、命令和网络权限分类。
- 定义确认请求、拒绝、超时和取消事件，但暂不注册有副作用的工具。
- 权限判定由宿主执行，不能依赖模型输出或控制 prompt。
- 为工作区外访问、符号链接替换和隐藏路径建立统一策略。

### Commit D：适配更强模型与协议评测

- [已落地] 固定 case schema、隔离工作区/Session、逐模型调用 trace 和分项汇总。
- [已落地只读子集] 适配 `primitive-bench` 的 18 个只读型任务和评分规则；写入、shell、
  测试类任务不计为当前模型失败。
- [待完成] 重复运行固定 13B baseline、版本化归档结果，并根据稳定性确定门槛。
- 覆盖直接回答、单工具、多工具、错误参数和越权请求。
- 输出动作合法率、任务完成率、平均 step、重试率、token 和耗时。
- 达不到预设门槛时保持实验性入口，不开放有副作用工具。

### Commit E：可写工具与扩展

- 协议评测稳定后先增加结构化 patch 工具，不直接开放任意 shell。
- 所有写操作展示精确目标和 diff，获得用户确认后执行。
- 写入后运行选定的只读验证命令；验证命令与写权限分开授权。
- 工具声明包含权限、超时、输出上限和可取消语义。
- 网络与外部插件保持显式启用，不作为本地 Agent 默认能力。

## 5. 完成定义

只读 Agent 里程碑只有在以下条件全部满足后才能标记完成：

1. 固定真实模型评测达到动作合法率和任务完成率门槛。
2. 多步任务可保存、退出、恢复，并保持 transcript/State revision 一致。
3. 取消、协议错误、工具错误和 step 超限均不留下伪完成记录。
4. 长任务有明确上下文预算和可观测的压缩行为。
5. `go test ./...`、`go test -race ./...` 与真实模型 Agent smoke test 通过。

在此之前，项目状态应保持“Phase 1 部分完成”。
