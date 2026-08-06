# 本地优先助手型 Agent 实施规格

状态：P0 代码与无模型闭环已落地；真实 13B 已复测，A4 为 0/5，未通过 P0 出口门槛
读者：直接实现本规格的人。每个 Commit 给出改动文件、签名、测试名和完成判据。
基线：`docs/agent-harness-milestone.md`（只读仓库 Agent，继续作为模型能力基线保留）
证据：`runs/api-13b-evaluation-report-20260803.md`

## 0. 怎么读这份文档

- Commit 编号即建议提交粒度。每个 Commit 结束时 `go build ./...` 与
  `go test ./...` 必须通过。
- 「新建」「修改」列出的路径是权威落点，不要另建平行目录。
- 签名给的是最小必要形状，可以加字段，不要改已给字段的语义。
- 判据里带「必须」的项是硬门槛，不满足就不算这个 Commit 完成。
- 所有阶段共同遵守第 2 节的原则，冲突时以第 2 节为准。

## 1. 为什么不能沿用 boundary suite

现有 18 题 `boundary`（`internal/agent/eval/boundary_cases.json`）是编程仓库任务，
`difficulty` 字段大量为 `single-tool-arithmetic`，题型是"读一个文件然后做硬推理"。
助手型产品的任务形状是多个浅事实、少量依赖、跨来源组装。

用 `boundary` 当产品门槛会持续低估进展：它测深度推理，产品测广度调度。因此：

| suite | 回答的问题 | 是否改动 |
|---|---|---|
| `boundary` | 补数据之后 13B 是不是变强了 | 不动 |
| `smoke` | 协议契约有没有回退 | 不动 |
| `assistant`（新增） | 产品能不能用 | 本规格新增 |

两条轨的分数永远不合并成一个数。

## 2. 原则

> 模型只做路由、拆解、参数生成；所有精确执行交给确定性工具；所有停止判断交给架构。

报告已证明 13B 在前三项稳定（协议 69/69、必需工具 21/22、route 18/18），在算术、
聚合、格式、停止上不稳定。这条原则让不稳定的部分不出现在关键路径上。

三条推论：

1. **模型输出是偏好，不是要求。**每个模型生成的值必须有确定性回退，回退链末端必须永远
   合法。
2. **不能确定性组装的才交给模型。**模板拼接、单位换算、时间比较一律用代码。
3. **失败必须显式。**未验证的结论必须标记，不能抹平成流畅回答。

## 3. 两个验证问题

这两题是整份规格的验收锚点，必须在确定性 mock 工具后端上可判分。天气每天都变，不能拿
真实 API 当判分基准。

### 3.1 问题 A：异构 + 跨波依赖

```
今天上海天气怎么样？我打算去最近的地铁站，但不知道它什么时候关门。
```

预期 DAG：

```
波次 1（并发）
  #1 weather(city="上海")
  #2 nearest_transit(kind="subway")
波次 2（依赖 #2）
  #3 transit_hours(station="$2.name")
```

判据：

| 判据 | 要求 |
|---|---|
| 子任务数 | 恰好 3 |
| 波次划分 | #1 与 #2 同波；#3 严格在 #2 之后 |
| 依赖表达 | #3 参数必须是 `$2.name` 引用，不能是字面站名 |
| 回答完整性 | 三个事实全部出现 |
| 输出格式 | 无协议标签、无 role label、无工具原始 JSON |

**主要陷阱**：模型直接写出一个幻觉站名，流程恰好也能跑通。因此依赖表达必须单独判分，
不能只看最终回答对不对。

### 3.2 问题 B：本地+网络混合 + 显式弃答

```
看一下我 notes 目录里这周的开销记录，一共花了多少，换成美元大概是多少？
```

预期 DAG：

```
波次 1
  #1 structured_query(path="notes/", filter="本周", aggregate="sum")
波次 2（依赖 #1）
  #2 fx_convert(amount="$1.total", from="CNY", to="USD")
```

判据：

| 判据 | 要求 |
|---|---|
| 本地求和 | 金额精确正确，且由 `structured_query` 算出而非模型心算 |
| 汇率可用 | 换算结果来自工具返回值 |
| 汇率不可用 | 必须给出人民币总额**并明确说明**美元换算未完成 |
| 禁止项 | 汇率不可用时编造汇率或美元数字 |

后两行是本题核心。参考项目 FRAMES 上 answered case 的无支撑断言率 15.52%——给了证据
仍然编。这一题防的就是这个。

### 3.3 为什么是这两题

- A 覆盖 planner、同波并发、引用替换。
- B 覆盖确定性计算、跨来源组装、必须走的降级路径。
- 都不需要开放网页搜索，不会被参考项目 16.75% 精确 URL 召回那个坑拖住。
- 都能在 mock 上完全确定性判分。

---

# P0：让现有 TUI 跑通这两题

现状核实：`go build ./...`、`go test ./internal/tui/... ./internal/agent/...` 均通过。
`internal/tui/agent/model.go` 已能显示 route、step、工具活动、取消、多轮。
**缺的不是 TUI，是它下面没有能回答这两题的工具。**

P0 全程不接真实网络，mock 先行以保证判分基准稳定。

## Commit A1：助手工具契约与 mock 后端

### 新建

```
internal/agent/tools/assistant.go          工具实现
internal/agent/tools/assistant_test.go
internal/agent/tools/mockdata/             确定性 fixture
internal/agent/tools/contract.go           工具契约测试套件
```

### 工具清单

沿用现有 `agent.Tool` 接口（`internal/agent/runner.go:51`），不新增接口。

| 工具 | Arguments | 返回字段 |
|---|---|---|
| `weather` | `{"city":"string"}` | `city`, `condition`, `temp_c`, `observed_at` |
| `nearest_transit` | `{"kind":"subway\|bus"}` | `name`, `distance_m`, `lines` |
| `transit_hours` | `{"station":"string"}` | `station`, `open`, `close`, `weekday` |
| `fx_convert` | `{"amount":"number","from":"string","to":"string"}` | `amount`, `rate`, `result`, `quoted_at` |
| `calculator` | `{"expression":"string"}` | `expression`, `result` |
| `structured_query` | `{"path":"string","filter":"string","aggregate":"sum\|count\|avg"}` | `matched_rows`, `total`, `excluded_rows` |
| `datetime` | `{"op":"now\|compare\|add","args":{...}}` | 依 op 而定 |

`structured_query` 的 `excluded_rows` 是刻意设计：报告里中文 JSONL 那题模型按用户整体
排除而非逐条过滤，工具显式返回被排除行可以让这类错误在 trace 里可见。

### 签名

```go
// internal/agent/tools/assistant.go
package tools

// Clock 让 datetime 与 "本周" 类过滤在测试中确定。
type Clock interface{ Now() time.Time }

// Provider 是所有外部数据的唯一入口。真实实现与 mock 实现都实现它。
type Provider interface {
    Weather(context.Context, string) (WeatherFact, error)
    NearestTransit(context.Context, string) (TransitFact, error)
    TransitHours(context.Context, string) (HoursFact, error)
    FXRate(context.Context, string, string) (RateFact, error)
}

// ErrProviderUnavailable 必须可被上层区分于参数错误。
var ErrProviderUnavailable = errors.New("provider unavailable")

type Options struct {
    Provider  Provider
    Clock     Clock
    Workspace string // structured_query 的根目录，复用 workspace 越界检查
}

func AssistantTools(Options) ([]agent.Tool, error)
```

### mock Provider

```go
// internal/agent/tools/mock.go
type MockProvider struct {
    Facts       MockFacts
    Unavailable map[string]bool // 键: "weather"|"nearest_transit"|"transit_hours"|"fx"
}
```

`Unavailable` 置位时返回 `ErrProviderUnavailable`，用于问题 B 的降级路径。

### 契约测试

```go
// internal/agent/tools/contract.go
type Suite struct {
    NewProvider func(*testing.T) Provider
    // 允许真实 Provider 跳过精确值断言，只校验字段存在与类型
    ExactValues bool
}
func Run(t *testing.T, suite Suite)
```

模式沿用 `internal/inference/contracttest/contract.go`：真实实现和 mock 共用同一套断言，
真实实现只放宽到「字段存在、类型正确、错误分类正确」。

### 判据

- `structured_query` 必须复用 `internal/agent/tools.go` 的 `workspace.resolve`
  越界检查，不得另写一份路径校验。
- 每个工具的 `Execute` 参数校验失败必须返回包 `ErrInvalidToolArguments` 的错误
  （现有 runner 靠它区分 schema 修复与运行时失败，见 `runner.go:477`）。
- `ErrProviderUnavailable` **不得**包装成 `ErrInvalidToolArguments`。
- `go test ./internal/agent/tools/...` 通过，mock 与真实实现跑同一 `contract.Run`。

## Commit A2：Provider 不可用的降级语义

### 修改

```
internal/agent/runner.go        新增不可用工具的提醒文案与标记
internal/agent/protocol.go      PrepareAnswer 注入未验证清单
```

### 要点

现有 `toolFailureReminder`（`runner.go:569`）把所有失败都当"换个工具或说明限制"。
Provider 不可用需要区别对待：不是参数错、不是路径猜错，重试没有意义。

```go
// runner.go
const rejectedProviderUnavailable = "provider_unavailable"
```

`Step` 增加一个字段，供 eval 与 TUI 读取：

```go
ToolUnavailable bool `json:"tool_unavailable,omitempty"`
```

答案阶段必须拿到"哪些事实没能验证"的显式清单。`PrepareAnswer` 现在只注入固定
control（`protocol.go:218`），改为可接受未验证项：

```go
PrepareAnswer(messages []Message, unverified []string) ([]Message, string)
```

这是接口变更，`ActionProtocol` 的所有实现和调用点都要跟着改。

### 判据

- Provider 不可用后，同一工具**不再被重试**，且不消耗 `maxConsecutiveToolFailures` 预算。
- 答案阶段 prompt 必须包含未验证项清单。
- 新增测试 `TestRunnerProviderUnavailableForcesExplicitLimitation`，断言输出提到限制且
  不含编造数字。

## Commit A3：assistant suite

### 新建

```
internal/agent/eval/assistant_cases.json
```

### 修改

```
internal/agent/eval/cases.go      新增 SuiteAssistant 与 AssistantCases()
internal/agent/eval/types.go      Expectation 新增 plan 维度；Metrics 新增计数
internal/agent/eval/runner.go     validateTurn 新增判据
cmd/rwkv-cli/main.go              --suite 接受 assistant
```

### Expectation 扩展

```go
// types.go
type Expectation struct {
    // ...现有字段保持不变...
    Plan *PlanExpectation `json:"plan,omitempty"`
    MustStateUnverified []string `json:"must_state_unverified,omitempty"`
}

type PlanExpectation struct {
    SubtaskCount int        `json:"subtask_count"`
    Waves        [][]string `json:"waves"`         // 每波的 tool 名，波内无序
    References   []Reference `json:"references"`   // 必须是引用而非字面值的参数
}

type Reference struct {
    Subtask  int    `json:"subtask"`   // 1-based
    Argument string `json:"argument"`  // 如 "station"
    Source   string `json:"source"`    // 如 "$2.name"
}
```

### Metrics 扩展

```go
// types.go Metrics
PlanSubtaskCount   Score `json:"plan_subtask_count"`
PlanWaveOrder      Score `json:"plan_wave_order"`
PlanReferenceUse   Score `json:"plan_reference_use"`
ExplicitAbstention Score `json:"explicit_abstention"`
PlanRejections     int   `json:"plan_rejections"`
PlanFallbacks      int   `json:"plan_fallbacks"`
```

P0 阶段还没有 planner，`Plan` 断言对 `inspect` 路径为空跳过。这个 Commit 先把判分维度
和 case 落地，P1 的 planner 直接被它测。

### 首批 case

必含：

| case ID | 形状 |
|---|---|
| `as_weather_transit_hours` | 问题 A |
| `as_expense_fx_convert` | 问题 B，汇率可用 |
| `as_expense_fx_unavailable` | 问题 B，汇率不可用，必须显式弃答 |
| `as_single_weather` | 单意图，**不得**触发扇出 |
| `as_two_independent_facts` | 多意图无依赖，两个子任务同波 |
| `as_ambiguous_needs_clarify` | 歧义，应追问而非猜 |

`as_single_weather` 是防过度规划的对照题。报告显示模型倾向多调用，新架构最大的新风险
是简单问题也付扇出成本。

### 判据

- `rwkv-cli agent-eval --suite assistant` 可运行，产物结构与现有 `run.json` /
  `trace.jsonl` / `summary.json` 一致。
- `answer_accuracy` 语义不变。新指标独立，不覆盖旧指标。
- 无模型单测覆盖新判分函数：`TestValidateTurnPlanExpectation`、
  `TestValidateTurnExplicitAbstention`。

## Commit A4：确定性计算层复测

### 动作

不改代码。把 A1 的 `calculator` 与 `structured_query` 注册进 `boundary` 的工具集，
用同一 13B、同一参数复测 18 题。

```bash
rwkv-cli agent-eval --model rwkv-g1i-13b-4922 --suite boundary \
  --output runs/boundary-with-compute-tools-<date>
```

### 为什么单独一个 Commit

这是整个计划里**唯一架构没动、只加了工具**的改动，因此是唯一能给出干净因果结论的地方。
报告里 5 个算术/聚合失败（`pb_loc_interest_8_months`、`pb_eur_trip_card_vs_fx`、
`pb_fx_column_trap`、`pb_jsonl_event_aggregate`、`pb_csv_reconcile_returns`）应该在这里
消掉。

### 判据

- 结果写入 `runs/`，并在 `docs/agent-harness-milestone.md` 追加一段实测记录。
- 5 个算术/聚合失败至少通过 3 个。**没达到就先别做 P1**，说明工具设计有问题。

### 2026-08-06 修订：`structured_query` 撤出 boundary

A4 的 0/5 结论中，3 题（`pb_csv_sum`、`pb_jsonl_event_aggregate`、
`pb_csv_reconcile_returns`）的失败原因是 `structured_query` 表达力不足，而不是模型不会拆解：
trace 显示模型意图每次都正确，是工具没有对应参数。`pb_csv_sum` 尤其明确——`sales.csv` 只有
`item,qty`，求和列硬编码为 `amount/total/value/revenue/result`，没有列参数，该题在原契约下
无论参数怎么写都必失败。

面对这个事实有两条路：加宽 `structured_query`，或让它退出 boundary。**选择后者。**理由是
boundary 这条轨道的存在意义就是测深度推理（第 1 节：`boundary` 回答「补数据之后 13B 是不是
变强了」），用一个能直接表达复合聚合的工具去覆盖它，等于把要考的东西替考掉，而且 A4
「只加确定性工具、架构不动」的干净因果口径也会被破坏。boundary 任务改由 `read_file` +
`calculator` 组合完成，考的是模型能不能把任务拆成正确表达式——这正是报告指出的真实弱项。

因此 A4 门槛的含义随之收窄：它现在只检验 `calculator` 能不能消掉纯算术失败
（`pb_loc_interest_8_months`、`pb_eur_trip_card_vs_fx`、`pb_fx_column_trap`），
另外 2 题的聚合能力改为在 assistant suite 用 `structured_query` 单独衡量。**5 题至少过 3
的原门槛不再适用于同一集合**，新门槛在复测后重定。`structured_query` 保持窄契约，
不为提分加宽。

### 2026-08-06 复测结果：A4 由 0/5 升至 2/5

详见 `runs/api-13b-v9-evaluation-report-20260806.md`。同一模型、同一 profile 下，A4 指定 5 题
`0/5 -> 2/5`，仍未达到原定 `>=3/5`。

实测推翻了本节的一个隐含前提。原判断是「模型算术不可靠，所以交给确定性工具」，但
`pb_jsonl_event_aggregate` 和 `pb_csv_reconcile_returns` 在**撤掉** `structured_query` 后仅用
`read_file` 就答对了，连 `calculator` 都没调用——模型自己的算术本来是对的，是不合身的工具把
它带偏了。因此第 2 节「所有精确执行交给确定性工具」需要补一条边界：**工具只有在能精确表达
任务时才优于模型直算；表达不了的工具会主动制造错误答案。**

仍失败的 3 题里，`pb_eur_trip_card_vs_fx` 和 `pb_fx_column_trap` **根本没有调用**
`calculator`。所以当前瓶颈不是「确定性工具算不对」，而是「模型不去用工具，或用了但表达式
拆错」。下一轮训练优先级应是「该算的时候去调工具」，而不是继续加工具。

## Commit A5：输出预算与答案结构校验

### 修改

```
cmd/rwkv-cli/main.go            --decision-max-tokens 默认 256 → 96
internal/agent/runner.go        答案阶段预算与结构校验
internal/agent/eval/runner.go   契约修复后指标
```

### 要点

参考项目 tool call 96 token、final answer 192 token。96 token 物理上没有空间加解释，
这直接治报告里两个"值对了但多说了话"的失败（`pb_markdown_release_notes` 与中文 flag 题）。

答案结构校验，落在 runner 提交答案之前：

```go
// runner.go
type answerViolation string

const (
    violationProtocolTag  answerViolation = "protocol_tag"
    violationRoleHeader   answerViolation = "role_header"
    violationJSONPayload  answerViolation = "json_payload"
    violationToolEcho     answerViolation = "tool_payload_echo"
)

func validateAnswer(output string) []answerViolation
```

校验失败**不是**直接放行也**不是**整轮失败，而是回退到显式弃答文案。

### 判据

- `answer_accuracy` 保持原始语义不变。
- 新增 `AnswerContractRepaired Score`，两个数在 `summary.json` 里都可见。
  否则会把模型弱点盖住，这一点是硬要求。
- 新增测试 `TestValidateAnswerRejectsProtocolTag` 等四条，每种 violation 一条。

## P0 出口条件

1. 问题 A、B（含汇率不可用变体）在 mock 后端上稳定通过。
2. `as_single_weather` 不触发多余工具调用。
3. A4 复测拿到确定性工具层的因果结论，5 个算术/聚合失败至少通过 3 个。
4. TUI 能完整走完两题，且降级说明可见。
5. `go test ./...` 与 `go test -race ./...` 通过。

### 2026-08-04 实测结论

- 脚本 mock 验收：问题 A、问题 B、汇率不可用变体全部通过。
- 真实 `rwkv-g1i-13b-4922` `assistant`：原始任务 1/6、回答 1/6、route 5/6、协议
  23/23、精确工具序列 1/5、参数 2/8。`as_single_weather` 通过；
  `as_two_independent_facts` 仅因日期格式被严格判分拒绝，语义口径约为 2/6。
- 真实 A4 `boundary`：总任务 8/18、回答 10/18；指定五题为 0/5，低于至少 3/5 的
  硬门槛。产物见 `runs/api-13b-v8-assistant-20260804-01/` 和
  `runs/api-13b-v8-boundary-compute-20260804-01/`。
- 因果结论：确定性执行层能工作，但 13B 尚不能可靠完成多步分解、参数生成和复杂聚合；
  `structured_query` 当前契约也不足以直接表达复合指标、分组、列选择和跨表计算。
- 判定：完成出口条件 1；真实单天气题满足条件 2；条件 3 明确失败；条件 4 尚未做真实 TUI
  手工验收。保持 P0，不开始 P1，不通过 Harness 语义特判抬分。

---

# P1：State fork 与并发扇出

## Commit B1：Session.Fork

### 现状

| 位置 | 状态 |
|---|---|
| `native/rwkv_agent_runtime/rwkv_agent_runtime.h:205` | `rwa_session_export_state` / `import_state` 可用 |
| `internal/inference/types.go:109` | `Fork(context.Context) (Session, error)` 已声明 |
| `internal/inference/backend/rwkvmobile/backend.go:663` | 返回 `ErrUnsupported` |
| `internal/inference/backend/mock/mock.go:384` | 返回 `ErrUnsupported` |
| capabilities | `StateFork` 已声明未赋值；只有 `StateExport`/`StateImport` 给了 `nativeSupport` |

export/import 已经能跑，Fork 是空的。填上它就拿到 root-prefill-once。README 记录
MLX FFI 有 16 个物理 State slot，CLI 开放 8 路。

### 实现

`backend.go:663` 的 `Fork` 改为：

1. 查 `available_state_slots`（header 第 83-84 行），不足则返回
   `wrap("fork session", inference.CodeCapacity, ...)`。
2. `m.native.NewSession()` 拿新 handle，失败按 `NewSession` 现有路径映射错误。
3. 父 session `ExportState` 到内存 buffer。
4. 新 session `ImportState`，descriptor 复用 `state.bin` 那套 codec / 尺寸 /
   prefix token / checksum 校验，**不另写一份**。
5. 注册进 `m.sessions`，失败路径必须 Close 掉半成品 handle。

mock 侧同样实现，用现有 `prefixTokens` + `revision` 做快照即可。

capabilities 补 `StateFork: nativeSupport`（native）与对应 mock 支持。

### 语义（写进接口注释）

Fork 是**快照分叉**，不是共享引用。父子独立推进、互不影响。这一点必须写清楚，否则后面
并发 worker 会有人以为改子状态能回传父状态。

### 测试

放进 `internal/inference/contracttest/contract.go`，mock 与 native 共用：

| 测试名 | 断言 |
|---|---|
| `ForkParentChildIndependent` | fork 后分别续写，改子不影响父的后续输出 |
| `ForkEquivalentToReplay` | fork 后续写结果 == 从头 replay 同段 transcript |
| `ForkAfterStopStringBoundary` | 在 stop string 处截断后 fork，仍满足等价性 |
| `ForkCapacityExhausted` | 超过 available 时返回 `CodeCapacity`，且已 fork 的 session 仍可用可 Close |

`ForkEquivalentToReplay` 是最关键的一条，它证明快照没丢东西。

`ForkAfterStopStringBoundary` 针对一个已知坑：参考项目
`docs/STATE_NATIVE_AGENT.md` 记录，非 EOS 的 stop token 必须提交进 state 再做下一次
续写，否则 resume 的 branch 与它实际生成的文本不等价。`</tool_call>` 正是 stop string，
扇出 worker 每一步都会碰到。

### 判据

- 四条契约测试在 mock 与 native 上都通过。
- fork 深度与并发宽度共享同一 slot 预算，且该约束可从 `Capabilities` 查到。
- `go test -race ./internal/inference/...` 通过。

## Commit B2：四模式调度

### 修改

```
internal/agent/route.go     Route 增加 fanout 与 plan
internal/agent/runner.go    按 Route 分流
```

### 分流表

| Route | 触发条件 | 做法 |
|---|---|---|
| `respond` | 不需要新证据 | 不变 |
| `inspect` | 单意图 | 不变。简单任务不付 planner 的额外调用与额外失败可能 |
| `fanout` | 同构多角度（多来源查同一件事） | 固定 mission 扇出，**无 planner** |
| `plan` | 异构多子任务（问题 A、B） | planner 输出 DAG |

`fanout` 借参考项目 `crates/agent-runtime/src/research.rs` 的做法：同一问题 prefill 一次、
fork 成 N 个 branch、每个 branch 挂一条固定 mission，没有模型生成的拆解结构。它们的四条
mission 是主要答案、官方来源、独立交叉验证、缺失与矛盾。

判断依据是**子任务是否同构**。同构走 `fanout`，异构才进 `plan`。这样 planner 的暴露面被
压到只有一条路径。

### 判据

- Router 输出四个值都能解析，非法值仍 fail closed 到 `respond`
  （沿用 `route.go:87` 现有语义）。
- `as_single_weather` 必须路由到 `inspect`，不得进 `fanout` 或 `plan`。

## Commit B3：planner 与 DAG 校验

### 新建

```
internal/agent/plan/plan.go       DAG 类型与校验
internal/agent/plan/plan_test.go
internal/agent/plan/protocol.go   planner 提示与解析
```

### 类型

```go
package plan

type Subtask struct {
    ID        int             `json:"id"`        // 1-based
    Tool      string          `json:"tool"`
    Arguments json.RawMessage `json:"arguments"`
    DependsOn []int           `json:"depends_on,omitempty"`
}

type Plan struct {
    Subtasks []Subtask `json:"subtasks"`
}

// Waves 按依赖分波。同波内可并发。
func (Plan) Waves() ([][]int, error)
```

### 校验规则

全部由 harness 执行，不依赖模型自觉：

```go
func Validate(p Plan, registry map[string]agent.Tool, maxSubtasks int) error
```

1. 子任务数 ≤ `maxSubtasks`（默认 6），超出直接拒绝。
2. 每个 `Tool` 必须在注册表存在。
3. 参数必须过工具 schema（复用工具自己的 `decodeArguments`）。
4. `DependsOn` 只能指向更小的 ID，检测环。
5. 校验失败 → 一次定向纠错重试 → 仍失败 fail closed 回退 `inspect`。

第 5 条沿用 `route.go` 里 Router 现有的 fail-closed 语义，保持一致。

### 引用替换

**跨波依赖必须用引用而不是值。**

```go
// 形如 "$2.name"：取子任务 2 结果的 name 字段
var referencePattern = regexp.MustCompile(`^\$(\d+)\.([a-z_][a-z0-9_]*)$`)

// Resolve 在上一波完成后替换引用。未解析的引用是错误，不是警告。
func Resolve(args json.RawMessage, results map[int]json.RawMessage) (json.RawMessage, error)
```

模型永远不需要凭空写出中间结果。这是问题 A 的核心判据，也是 planner 唯一被允许表达
依赖的方式。字面值出现在依赖位置必须判为失败，即使最终答案正确。

### 判据

- 五条校验规则各有单测，环检测单独一条。
- `TestResolveRejectsLiteralInDependentPosition`。
- planner 校验失败率与 fallback 率进入 `Metrics`（A3 已预留字段）。

## Commit B4：确定性回退链

### 新建

```
internal/agent/fallback/chain.go
internal/agent/fallback/chain_test.go
```

### 要点

参考实现 `src/rwkv_agent/query_coordinator.py` 的 `coordinate()`：模型生成的值只是候选
之一，逐个过校验，第一个通过的就用，**回退链末端永远合法**。

```go
type Candidate struct {
    Value    string
    Strategy string // "model" | "anchors" | "raw" ...
}

// Coordinate 返回第一个通过校验的候选。末端候选必须无条件合法。
func Coordinate(candidates []Candidate, validate func(string) []string) (Candidate, []string)
```

这比当前"拒绝 + 重试 + fail closed"强一档：当前是模型错了就重试、重试还错整轮降级；
回退链是模型错了就用确定性替代品，**流程不中断**。报告里 12 次重复调用被拒、14 次强制
回答，在这个结构下变成静默降级。

两条纯集合运算的校验直接搬（参考 `src/rwkv_search/search_reasoning.py:510`）：

| 检查 | 规则 |
|---|---|
| `subject_drift` | 生成值必须保留原问题至少一个 anchor |
| `ungrounded_constraint` | 出现的约束必须在原问题或已有观察里出现过 |

第二条正好治报告里"给 `search_text` 幻觉出不支持的 `after` 参数"。**只删不加**——不许
模型加入凭空约束，但保留它的有用改写。

### 判据

- `TestCoordinateFallsBackToTerminalCandidate`：模型候选全非法时仍返回合法值。
- `TestUngroundedConstraintRejected`：凭空出现的参数被删掉而非整体拒绝。

## Commit B5：TUI 扇出视图

### 修改

```
internal/agent/runner.go        新增 plan/subtask/wave 事件
internal/tui/agent/model.go     recordEvent 处理新事件
internal/tui/agent/view.go      DAG 与波次渲染
```

### 新事件

现有 `EventKind`（`runner.go:80`）不够，补：

```go
EventPlanStart    EventKind = "plan_start"
EventPlanDone     EventKind = "plan_done"     // 携带子任务数与波次划分
EventWaveStart    EventKind = "wave_start"
EventSubtaskDone  EventKind = "subtask_done"  // 携带 verified 标记
```

`Event` 结构相应增加 `Subtask int`、`Wave int`、`Verified bool`。

### 渲染要求

- 子任务列表 + 依赖关系 + 每个子任务状态。
- 当前第几波、波内并发几路。
- 每个子任务的 `verified` 标记，未验证项在最终回答里可追溯。

### 判据

- `internal/tui/agent/pty_test.go` 新增扇出场景，断言 DAG 与波次可见。
- 未验证子任务在 TUI 上有区别于成功的视觉标记。

---

# P2：早停与真实网络

## Commit C1：证据充分早停

每波结束后确定性判断证据是否已覆盖所有子任务，够了直接进 reduce。

这是参考项目的 P1 未解决项：固定轮数不早停，Fresh-Web P95 42.33 秒、200 个请求
**全部**超出 20 秒预算，`docs/KNOWN_ISSUES.md` 明确写了
`state research lacks evidence-sufficiency early stop`。从一开始就有，别等到那个数字出现。

判据：`Metrics` 新增早停触发率；有早停与无早停的 A/B 延迟对比进 `runs/`。

## Commit C2：权限契约

网络工具需要先有 `docs/agent-harness-milestone.md` Commit C 的权限分类。按那份文档，
网络能力必须显式启用、不作为默认。此 Commit 是那份 checklist 的落地，不重复设计。

## Commit C3：真实 Provider

替换 mock Provider 为真实实现，**判分基准仍用 mock**，避免真实 API 波动污染回归。
真实实现只跑 `contract.Run` 的放宽子集（字段存在、类型正确、错误分类正确）。

## 工具优先级按抽取损失排

| 类别 | 抽取损失 | 优先级 |
|---|---|---|
| 结构化 API（天气、交通、汇率、时区） | 无 | 先做 |
| 本地文件与索引 | 无 | 先做 |
| 开放网页搜索 | 参考项目实测极大 | 最后，且必须带早停 |

参考项目投入 SearXNG 多 lane + Dogpile + Naver + GitHub + MediaWiki + Crossref +
Bing fallback + 可选 Tavily + bounded fetch + 静态抽取 + Evidence 构建，换来：

| 指标 | 值 |
|---|---:|
| Gold 域名召回 | 81% |
| 精确 URL 召回 | 16.75% |
| 答案 Token F1 | 11.19% |
| 无支撑断言率（FRAMES answered） | 15.52% |

找到正确域名 81%，把答案捞出来 11%。瓶颈不在 agent 循环、不在工具协议、不在扇出并发，
而在证据选择和有据生成，他们自己的发布门槛没过。所以开放网页搜索不能是本产品核心，
只能是后置兜底。

---

# 不做的事

- 不复制参考项目的检索栈规模。
- 不做固定轮数无早停的扇出。
- 不把 Rust 控制面 + Python 数据面 + sidecar + scheduler 那套搬进来；当前单 Go 二进制
  在这个目标下够用。
- 不为了端到端分数好看，把拆解和整理都移到云端。云端只能是可选层：planner 接口后面挂
  本地与云端两个实现跑 A/B，云端当**天花板参照**，本地报告差距，差值即下一轮补数据的
  目标。默认路径必须本地，否则离线即失效，且永远不知道本地 planner 行不行。

# 要保住的既有优势

改架构时不能退化：

| 项 | 本项目 | 参考项目 |
|---|---|---|
| 工具协议合法率 | 69/69 | 92.5%（40 个 BFCL 里 3 个 JSON 不合法） |
| 工具参数复杂度 | 多字段仍 100% 正确 | 三个工具全是单 `query` 字符串 |
| 事务性 | `ErrNoWorkspaceEvidence` 整轮回滚 | 仅 answer 阶段校验失败后回退固定文案 |

协议合法率来源是 prefill `<tool_call>` + greedy + 严格 envelope 解析，参考项目的 P0
backlog 第一条正在补这个。**不要因为"他们更简单"而简化工具 schema。**

# 指标与门槛

沿用"分层不塌陷成一个数"（参考项目 `CLAUDE.md` 明确要求；本项目
`pb_config_precedence_resolve` 已出现 harness 判分严与模型错混淆）：

| 层 | 指标 |
|---|---|
| planner | 子任务数正确率、波次划分正确率、依赖引用正确率、校验拒绝率、fail-closed 率 |
| 执行 | 工具成功率、降级触发次数、早停触发率 |
| 输出 | `answer_accuracy` 原始值、契约修复后值、显式弃答正确率、无支撑断言率 |
| 成本 | 模型调用次数、prompt/completion token、P50/P95 延迟、fork 节省的 prefill |

助手型门槛在 assistant suite 稳定之后再定。在此之前不开放有副作用的工具，入口保持
实验性。
