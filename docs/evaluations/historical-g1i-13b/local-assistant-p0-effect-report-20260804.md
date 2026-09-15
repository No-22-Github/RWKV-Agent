# 本地优先助手 Agent P0 落地效果报告

日期：2026-08-04  
实现提交：`d09fba2 feat: add local assistant P0 harness`  
模型：`rwkv-g1i-13b-4922`  
Harness：`rwkv-agent-eval-v8`  
协议：`rwkv-g1i-envelope-v1` / `rwkv-g1i-route-v1`  

## 1. 结论

P0 已完成代码落地和无模型闭环，但没有通过产品出口门槛。

- Agent 循环已经从仓库只读工具扩展到本地助手形状，并具备确定性计算、Provider 不可用
  降级、答案协议泄漏保护和更细的评测归因。
- 13B 的 route 和工具控制协议稳定：assistant 为 `23/23`，boundary 为 `77/77`，两轮均
  没有协议重试或 Router fallback。
- 单天气工具题通过；两个独立事实题能正确调用两个工具，但最终合成遗漏了具体时间。
- 多步依赖、参数生成、歧义澄清、复杂聚合和财务分解仍明显不足。
- A4 指定的五个算术/聚合失败为 `0/5`，没有达到至少 `3/5` 的硬门槛。
- 增加确定性工具没有自动提高端到端分数。执行器能精确执行表达式，但模型尚不能稳定地产生
  正确的表达式和查询参数。

因此当前成果应定义为“可测试、可降级、可诊断的 P0 Agent 循环”，不能定义为“已经可用的
本地助手”，也不能据此进入 P1 或开放有副作用工具。

## 2. 这次具体落地了什么

### 2.1 助手工具层

新增七个只读或确定性工具：

| 工具 | 作用 | 当前数据边界 |
|---|---|---|
| `weather` | 按城市查询天气 | 固定 mock Provider |
| `nearest_transit` | 查询最近公交/地铁站 | 固定 mock Provider |
| `transit_hours` | 查询站点运营时间 | 固定 mock Provider |
| `fx_convert` | 使用 Provider 汇率换算 | 固定 mock Provider |
| `calculator` | 执行有限算术表达式 | 本地确定性执行 |
| `structured_query` | 读取 JSON/JSONL/CSV 并做过滤、求和、计数、平均 | 工作区内本地执行 |
| `datetime` | 查询当前时间或时区转换 | 本地时钟 |

天气、交通和汇率目前没有接真实网络。它们验证的是 Provider 接口、工具调用和降级链路，
不是实时数据能力。

`structured_query` 复用现有工作区越界检查。当前契约只支持：

- 空过滤；
- `本周` / `this week`；
- 逗号或 `&&` 连接的精确 `field=value`；
- 单一 `sum|count|avg` 聚合。

它暂不支持比较表达式、指定聚合列、分组、多指标或跨表计算。

### 2.2 Agent 循环

本次运行时改进包括：

1. Router 从“是否需要仓库文件”扩展为“是否需要新的只读工具证据”，覆盖外部事实、
   本地文件和确定性计算。
2. 缺少城市等必要参数时，Router prompt 要求走 `respond` 追问，而不是猜测。
3. Provider 不可用会被标记为不可重试；Runner 强制进入回答阶段，并注入未验证事实清单。
4. 最终回答提交前检查协议标签、role header、整段 JSON 和原始工具 payload。
5. 若答案违反展示契约，用户 transcript 写入确定性 fallback，同时评测保留模型原文，避免
   安全修复掩盖模型弱点。
6. 第一次工具决策预算从 256 token 降到 96 token，减少简单控制帧继续生成废话的空间。
7. `structured_query` 不再把 `date >= ...` 误解析成字段名并静默返回 0；不支持的运算符会
   明确返回参数错误。

这些改动提高的是同一个模型在当前 Harness 中的有界性、失败可见性和输出安全性，没有修改
模型权重，也没有新增 planner。评测中的 `Plan` 字段只是为后续 planner 预留的观测结构。

### 2.3 评测层

新增 6-case `assistant` suite 和 schema v3，分开记录：

- task success / answer accuracy；
- route / protocol；
- 精确工具序列和参数；
- 必需工具和必需调用；
- no-call / 显式弃答；
- plan 占位指标；
- 答案契约修复率；
- 工具请求、实际执行、错误、重复拒绝和强制回答。

这部分不直接改善 Agent 运行效果，但能把模型、Harness、工具契约和判分器的问题分开。

## 3. 评测配置与证据

两组远程评测使用同一模型和采样配置：

| 配置 | 值 |
|---|---|
| model | `rwkv-g1i-13b-4922` |
| completion | `rwkv-lightning` |
| sampling | greedy，`top_k=1`、`top_p=1` |
| reasoning / few-shot | 关闭 / 关闭 |
| max steps | 6 |
| protocol / route retries | 1 / 1 |
| route / decision / answer tokens | 16 / 96 / 1024 |
| environment | macOS arm64，Go 1.26.5 |

原始产物：

- `runs/api-13b-v8-assistant-20260804-01/run.json`
- `runs/api-13b-v8-assistant-20260804-01/trace.jsonl`
- `runs/api-13b-v8-assistant-20260804-01/summary.json`
- `runs/api-13b-v8-boundary-compute-20260804-01/run.json`
- `runs/api-13b-v8-boundary-compute-20260804-01/trace.jsonl`
- `runs/api-13b-v8-boundary-compute-20260804-01/summary.json`

认证信息没有写入代码、报告或评测产物。服务端 usage 仍全部为 0，因此本轮不能评价 token
效率，也不能从 usage 判断具体阶段是否命中输出预算。

## 4. Assistant Suite 效果

### 4.1 汇总

| 指标 | 结果 |
|---|---:|
| 原始任务通过 | 1/6 |
| 原始答案正确 | 1/6 |
| 按当前 case 契约校正日期格式后 | 2/6 |
| 按用户原句的完整产品语义 | 约 1/6 |
| Route 正确 | 5/6 |
| 协议合法 | 23/23 |
| 精确工具序列 | 1/5 |
| 参数正确 | 2/8 |
| 必需工具 | 2/2 |
| 必需调用 | 2/2 |
| No-call | 0/1 |
| 模型请求 | 29 |
| 工具请求 / 实际执行 | 17 / 16 |
| 工具错误 | 5 |
| 重复调用被拒绝 | 1 |
| 强制回答 | 3 |
| 协议重试 / Router fallback | 0 / 0 |
| 总耗时 | 60.9 秒 |

`2/6` 只表示按当前 case 契约修正中文日期格式后通过。用户原句要求“日期时间”，模型最终
只写日期、没有写 `10:00`，所以按更严格的产品语义仍不能算完整通过。汇率不可用题虽然正确
拒绝猜测，但本地总额错误，也不能整体改判为通过。

### 4.2 逐题结果与归因

| Case | 期望 | 实际工具轨迹 | 实际回答摘要 | 判定与主要归因 |
|---|---|---|---|---|
| `as_weather_transit_hours` | `weather -> nearest_transit -> transit_hours`；回答世纪大道站、23:30 | `weather -> transit_hours` | 天气正确；把“上海”当站点，未取得运营时间 | 失败。模型跳过依赖步骤，参数传递失败；Harness 正确返回工具错误 |
| `as_expense_fx_convert` | `structured_query(本周) -> fx_convert(150)`；150 CNY / 21 USD | `list_files -> read_file -> structured_query -> structured_query -> fx_convert` | 100 CNY / 14 USD | 失败。模型生成不支持的过滤条件，修复时只筛 `amount=100`；执行器按参数正确执行 |
| `as_expense_fx_unavailable` | 先得到 150 CNY；FX 不可用时明确弃答 | `list_files -> read_file -> structured_query -> structured_query -> fx_convert` | 本地总额 0；明确说明 Provider 不可用 | 失败。模型先生成不支持语法；旧过滤器又静默返回 0，模型与 Harness 都有责任；降级语义正确 |
| `as_single_weather` | 单次 `weather(上海)` | `weather` | 多云、27°C | 通过。当前最稳定的助手形状 |
| `as_two_independent_facts` | `weather` 与 `datetime`，无依赖；回答日期和时间 | `weather -> datetime` | `2026年8月4日`、多云、27°C，遗漏 `10:00` | 旧 scorer 因日期格式判失败确有误伤；但 case 本身也漏验“时间”，按产品语义仍不完整 |
| `as_ambiguous_needs_clarify` | `respond`，追问城市，不调用工具 | `weather -> weather` | 擅自回答北京晴、30°C | 失败。模型没有遵守歧义澄清规则，并重复调用天气；这是模型/Prompt 遵循问题 |

### 4.3 可以确认的提升

- 单工具助手事实题能稳定走完工具闭环。
- 两个独立工具可以顺序调用并取得正确结果，但最终合成仍可能漏字段。
- Provider 不可用时，最终回答能明确拒绝猜测该事实。
- 工具控制帧在 23 个动作中全部合法，新增助手工具没有破坏协议稳定性。
- 本轮没有答案协议泄漏，也没有触发安全 fallback。

### 4.4 仍未解决的问题

- 模型不能稳定构造“先找站点，再用站点名称查运营时间”的依赖链。
- 模型倾向于先 `list_files/read_file`，没有直接使用更高层的 `structured_query`。
- 工具参数语法不熟悉，错误修复会缩小到错误的数据子集。
- Router prompt 已要求歧义时追问，但真实模型仍猜城市，说明仅靠 prompt 不可靠。
- 没有显式 planner；当前仍由模型逐步决定下一动作。

## 5. A4 确定性计算层复测

### 5.1 汇总

| 指标 | v7 基线（2026-08-03） | v8 + 计算工具（2026-08-04） |
|---|---:|---:|
| 任务通过 | 10/18 | 8/18 |
| 答案正确 | 11/18 | 10/18 |
| Route 正确 | 18/18 | 18/18 |
| 协议合法 | 69/69 | 77/77 |
| 必需工具 | 21/22 | 19/22 |
| 必需调用 | 22/23 | 20/23 |
| 工具请求 / 实际执行 | 51 / 39 | 60 / 47 |
| 工具错误 | 15 | 22 |
| 重复调用被拒绝 | 12 | 13 |
| 强制回答 | 14 | 16 |
| 总耗时 | 129.8 秒 | 186.1 秒 |

这不是严格 A/B：v8 增加了工具、Provider/答案状态、评测字段，并把第一次决策预算从 256
降到 96 token。表格只能说明“当前整体结果没有改善”，不能把两题下降单独归因于某一个改动。
v8 相比 v7 新失去 `pb_csv_sum` 和 `pb_missing_file_recover`；其余八个通过 case 保持一致。

### 5.2 五个目标失败

| Case | 正确答案 | v8 实际轨迹 | 实际答案 | 归因 |
|---|---|---|---|---|
| `pb_loc_interest_8_months` | `289.13` | `read_file -> calculator -> calculator` | `30.33` | calculator 正常；模型只计算单段，没有汇总八个月 |
| `pb_eur_trip_card_vs_fx` | `EUR by 2686.00` | `read_file -> calculator x4` | `EUR by 12.15` | 模型拆解和百分比/金额映射错误，不是执行精度问题 |
| `pb_fx_column_trap` | `28079.50` | `read_file -> structured_query -> read_file` | `27498.5` 且附完整过程 | 工具不支持该纯文本复合计算；模型回退后选错汇率列并违反输出格式 |
| `pb_jsonl_event_aggregate` | `orders=6 users=5 revenue=438.72` | `read_file -> structured_query x3` | `orders=5 users=4 revenue=355.72` | 模型请求不支持的 SQL 风格过滤和复合聚合，随后手工汇总仍错误 |
| `pb_csv_reconcile_returns` | `SKU-17 1248.50` | `read_file -> structured_query x2` | `SKU-17` | 当前工具不能表达跨表、乘法、分组和退款抵扣；模型只给出 SKU |

结果是 `0/5`，低于 P0 要求的 `>=3/5`。

### 5.3 因果结论

确定性工具解决了“给定正确表达式后如何精确执行”，没有解决以下模型任务：

1. 从自然语言和文件中识别全部变量；
2. 选择正确列和业务方向；
3. 把多段计算组合成一个完整表达式；
4. 生成工具实际支持的参数；
5. 判断工具结果是否完整；
6. 按用户要求输出严格格式。

`structured_query` 本身也过窄。对于多指标、分组、列选择和跨表问题，模型即使理解任务也
无法通过当前契约一次表达。继续增加 prompt 文字或 MaxSteps 不足以解决这个边界。

## 6. 模型、Harness 与 Scorer 归因

### 6.1 模型侧

- 依赖分解不稳定；
- 参数生成与工具 grammar 不匹配；
- 错误恢复时容易改成“可执行但语义错误”的参数；
- 不会可靠澄清缺失参数；
- 复杂聚合、财务映射和严格格式仍弱；
- 证据充分后的停止判断仍不稳定。

### 6.2 Harness / 工具侧

- 旧 `structured_query` 曾把 `date >= ...` 静默解析成错误字段，造成可信的 0；现已修复为
  明确拒绝。
- 当前查询契约不能表达列选择、比较、分组、多聚合和跨表关系。
- mock Provider 只能证明循环和降级，不能证明实时产品能力。
- 没有 planner、依赖图或并行工具调度。

### 6.3 Scorer 侧

- `as_two_independent_facts` 原来只接受 ISO 日期，误伤语义等价的中文日期；现已增加二选一
  判分。但当前 case 仍只验证日期，没有验证回答必须包含具体时间，后续应补上该断言。
- FX 降级原来要求固定词“未完成”，误伤“Provider 不可用，无法换算”；现改为检查
  “不可用”。
- 这些修复发生在远程产物生成之后。报告保留原始 1/6，不离线重算冒充新远程结果。

## 7. P0 出口检查

| 出口条件 | 状态 | 证据 |
|---|---|---|
| 问题 A、B 和 FX 不可用变体在 mock 后端稳定通过 | 通过 | 脚本 continuation acceptance 3/3 |
| 单天气题不触发多余工具 | 通过 | 真实 13B `weather` 一次调用 |
| 五个算术/聚合失败至少通过三个 | **失败** | A4 为 0/5 |
| TUI 真实走完两题且降级可见 | 未完成 | 仅完成脚本和 `agent-eval` 验收 |
| `go test` 和 race 通过 | 通过 | 提交前全量验证通过 |

最终判定：P0 代码已落地，P0 产品门槛未通过。

## 8. 下一步建议

优先级按当前证据排序：

1. 设计通用的 `structured_query` v2 契约，至少明确 `select`、`where`、`group_by`、多聚合和
   数值表达式边界；不要按 benchmark case 增加特判。
2. 为模型补充依赖传参轨迹：`weather + nearest_transit -> transit_hours($station.name)`，
   训练结果引用而不是猜参数。
3. 补充工具 grammar 修复数据：只使用 schema 中存在的字段；不支持时换策略，不重复提交
   相同无效调用。
4. 补充歧义澄清数据：城市、币种、目录等必要参数缺失时直接追问，不调用 Provider。
5. 补充“证据是否充分”的正反例，训练 call / continue / stop / recovery，而不是提高
   `MaxSteps`。
6. 用修复后的过滤器和 scorer 重跑 assistant suite；至少重复三轮，分别报告原始严格分和
   语义复核分。
7. 完成真实 TUI 手工验收，再决定是否接入真实 Provider。真实 Provider 仍应保留相同的
   unavailable 契约、超时、取消和权限边界。

在 A4 达到门槛前，不进入 P1，不开放写文件、shell、Git 或真实网络副作用工具。
