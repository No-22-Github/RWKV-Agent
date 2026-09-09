# Wire Spec 重构 P0：冻结基线与 legacy → Spec 映射

状态：**草案，待确认**（P0 交付物）
基线：`go test ./internal/agent/... ./api/... ./cmd/rwkv-cli/...` 全绿（2026-09-08，Go 1.27.1）
上游设计：见对话中确认的「轴 + 简写」模型；本文件把它落成可 review 的清单。

---

## 0. P0 不变量与验收

1. **不改任何 prompt 字节。** 现有 `internal/agent/testdata/golden_prompt/` 7 个文件必须逐字节不变。
2. **不改题库、case schema、旧 CLI flag 语义。** 旧 flag 全部保留，只重新归类为轴的长写别名。
3. **本阶段只产出映射与基线**，不引入 `Spec` 类型（P1 才落代码）。

验收：

- [x] 现有测试全绿（记录于本文件头部）
- [ ] 本文件的轴定义、legacy 映射、可达组合、约束表、golden 矩阵逐项确认
- [ ] P1 的验收标准（§7）确认

---

## 1. 轴定义（9 个用户可见轴）

| # | 轴 | 取值 | 现状载体 | 默认来源 | 备注 |
|---|---|---|---|---|---|
| 1 | `format` | `xml` \| `md-fence` | `--agent-protocol` | App/agent: `xml`；agent-eval: `markdown`；primitive 强制 `md-fence` | 线格式，不含 transport |
| 2 | `thinking` | `off` \| `fast` \| `full` | `--thinking` / `--reasoning` | `off` | `md-fence` 产品 transcript 只支持 `off` |
| 3 | `prefill` | `none` \| `envelope` \| `fence` \| `deep-fence` \| `fake-think-half` \| `fake-think-closed` | `--deep-tool-anchor`、`--decision-fake-think`、`--closed-fake-think`、router 联动 | md 产品: `deep-fence`；xml: `none`；primitive: renderer 自带 fence | 单槽位轴，见 §4 |
| 4 | `abstain` | `none` \| `no-tool` \| `no-tool+gate-state` \| `no-tool+gate-evidence` | `--semantic-no-tool`、`--no-tool-gate` | md 产品: `no-tool`；xml: `none` | `no_tool` 在两种 transcript 都实现 |
| 5 | `terminal` | `none` \| `submit` | `Options.TerminalTool/EndOnTerminalTool`；primitive 逐题 | 产品: `none`；primitive: 逐题 | |
| 6 | `route` | `none` \| `respond-inspect` \| `progressive` | `--route-stage`、`--progressive-tools` | 全部默认 `none`；bfcl-product 默认 `progressive` | 7B/13B 实测可不用；本轮只保留不改 |
| 7 | `catalog` | `full` \| `progressive` | `--progressive-tools` | `full` | 与 `route=progressive` 强耦合（当前同一开关） |
| 8 | `control` | `base` \| `fewshot` | `--few-shot` | `base` | 只影响 XML 指令与 PostToolReminder |
| 9 | `loop` | 结构化（见 §1.1） | `--max-steps`、`--decision-max-tokens`、`--duplicate-*`、`--same-tool-rescue-limit`、`--answer-stage-lead` 等 | 见 §1.1 | **兜底机制靠循环计数触发，必须入 Spec** |

### 1.0 实现轴（默认隐藏，不在首轮 CLI 暴露）

| 轴 | 取值 | 来源 | 备注 |
|---|---|---|---|
| `transcript` | `product` \| `benchmark` | `G1IFunctionProtocol.Product` / `G1IFunctionRenderer.Product` | benchmark = submit 终止的训练 transcript；产品 Markdown 也是 `md-fence`，两者只差这个轴 |
| `transport` | `text` \| `native` | `chat-prompt-mode=native-chat`（由 generator 探测） | 不放进 `format`：native 只替换调用通道，control/answer/tool-result 仍由文本格式决定；且 native 提供 tools 时没有 prefill |
| `feedback` | `raw` \| `compress-fetch` | `--compress-fetch` | 改进入 transcript 的字节 |
| `subagent` | `block` \| `raw` | `--subagent-raw-feedback` | 同上 |


### 1.1 `loop` 轴字段

| 字段 | 现状 flag / 常量 | 产品值 | eval CLI 默认 | primitive |
|---|---|---|---|---|
| `MaxSteps` | `--max-steps` | 6（App config） | 6 | 逐题 `max_turns`（6–22） |
| `ProtocolRetries` | 无 flag | 1 | 1 | 1 |
| `RouteRetries` | 无 flag | 0/1（progressive 时 1） | 1（route-stage） | — |
| `DecisionMaxOutputTokens` | `--decision-max-tokens` | min(config, max) | 0 → 按 protocol 默认 | `= AnswerMaxOutputTokens`（1024） |
| `AnswerMaxOutputTokens` | `--max-tokens` | 1024（agent 默认） | 1024 | 1024 |
| `RouteMaxOutputTokens` | `--route-max-tokens` | 48 | 16，bfcl-product 重置 48 | — |
| `DuplicateReplayLimit` | `--duplicate-replay-limit` | 2 | 2 | 2 |
| `DuplicateRescueThreshold` | `--duplicate-rescue-threshold` | 3 | 3 | 3 |
| `SameToolRescueLimit` | `--same-tool-rescue-limit` | **3** | **3**（已统一到 `ProductSameToolRescueLimit`） | 3（upstream 因 `AllowRepeatedCalls` 实际不触发救援，go-native 触发） |
| `AnswerStageLead` | `--answer-stage-lead` | 0 | 0 | 0 |

> **已解决（2026-09-08）**：同一个「同工具连续成功」兜底，产品 3 / eval CLI 8 的 drift 已统一到
> `agent.ProductSameToolRescueLimit = 3`；历史 eval 值 8 保留为**显式实验值**，
> 需要时显式传 `--same-tool-rescue-limit 8`。代价是 `boundary/smoke/assistant/primitive` 的
> 兜底会更早触发，历史分数可能变化（用户已确认接受）。
> 独立的 `bfcl-multiturn` 命令仍是自己的 12（该 harness 的 GT 会自然跑出 4–31 的 same-tool
> 连续段，不能用产品常量），不在本次统一范围内。

### 1.2 候选次轴（待确认，P0 暂不纳入 Spec）

| 候选轴 | 取值 | 现状 | 影响 |
|---|---|---|---|
| `feedback` | `raw` \| `compress-fetch` | `--compress-fetch` | 改的是进入 transcript 的字节 |
| `subagent-feedback` | `block` \| `raw` | `--subagent-raw-feedback` | 同上 |
| `transport` | `local` \| `rwkv-lightning` \| `chat-completions` | `--completion` 等 | provider 层，但与 `format=native` 有约束关系 |

---

## 2. legacy flag → 轴映射

### 2.1 格式与预填

| 旧 flag / 输入 | 映射 |
|---|---|
| `--agent-protocol xml` | `format=xml` |
| `--agent-protocol markdown` | `format=md-fence` |
| `--completion chat-completions --chat-prompt-mode native-chat` | `format=native`（transport=native） |
| `--thinking off\|fast\|full` | `thinking` |
| `--reasoning[=true]` | `thinking=fast`（deprecated alias） |
| `--deep-tool-anchor` | `prefill=deep-fence`（未设时按 format 取默认） |
| `--decision-fake-think` | `prefill=fake-think-half` |
| `--decision-fake-think --closed-fake-think` | `prefill=fake-think-closed` |
| `--closed-fake-think`（无 fake-think） | 报错（现状） |
| （XML + router + inspect） | `prefill=envelope` |
| （md 非 respond 路由） | `prefill=fence`（浅锚点默认） |
| （answer 阶段） | 由 format 派生，不是轴值 |

### 2.2 动作空间与终止

| 旧 flag | 映射 |
|---|---|
| `--semantic-no-tool` | `abstain=no-tool` |
| `--no-tool-gate state` | `abstain=no-tool+gate-state` |
| `--no-tool-gate evidence` | `abstain=no-tool+gate-evidence` |
| （primitive 题目含 `submit`） | `terminal=submit` |
| `--progressive-tools` | `route=progressive`, `tools=progressive` |
| `--route-stage` | `route=respond-inspect` |
| `--few-shot` | `control=fewshot` |

### 2.3 循环

| 旧 flag | 映射 |
|---|---|
| `--max-steps` | `loop.MaxSteps` |
| `--decision-max-tokens` | `loop.DecisionMaxOutputTokens`（0 = 按 format 默认） |
| `--max-tokens` | `loop.AnswerMaxOutputTokens` |
| `--route-max-tokens` | `loop.RouteMaxOutputTokens` |
| `--duplicate-replay-limit` | `loop.DuplicateReplayLimit` |
| `--duplicate-rescue-threshold` | `loop.DuplicateRescueThreshold` |
| `--same-tool-rescue-limit` | `loop.SameToolRescueLimit` |
| `--answer-stage-lead` | `loop.AnswerStageLead` |

### 2.4 不入 Spec（provider / 评测夹具）

`--model`、`--tokenizer`、`--backend`、`--provider`、`--completion` 的 endpoint/auth 部分、
`--api-*`、`--state-id`、`--web`、`--subagents`、`--*-fixture`、`--file-tools`、`--primitive-profile`、
`--case-*`、`--output`、采样参数（`--temperature` 等）。

---

## 3. 当前可达组合清单（P1 必须逐一保住）

| # | cell | format | thinking | prefill | abstain | terminal | route | 入口 |
|---|---|---|---|---|---|---|---|---|
| 1 | App/agent 默认 XML | xml | off | none | none | none | none | `api`, `agent` |
| 2 | XML + thinking | xml | fast/full | none | none | none | none | `--thinking` |
| 3 | XML + XML 兼容 router | xml | off | envelope | none | none | respond-inspect | `agent-eval --route-stage` |
| 4 | 产品 Markdown 默认 | md-fence | off | deep-fence | no-tool | none | none | `agent --agent-protocol markdown`, App markdown |
| 5 | Markdown 浅锚点 | md-fence | off | fence | no-tool | none | none | 显式关闭 deep anchor |
| 6 | fake-think 实验 | md-fence | off | fake-think-half/closed | no-tool | none | none | `--decision-fake-think` |
| 7 | bfcl-product Markdown | md-fence | off | deep-fence | no-tool | none | progressive | `agent-eval --suite bfcl-product` |
| 8 | bfcl-product XML | xml | off/fast/full | none | none | none | progressive | `--agent-protocol xml` |
| 9 | bfcl-product + gate | md-fence | off | deep-fence | no-tool+gate-* | none | progressive | `--no-tool-gate` |
| 10 | boundary/smoke/assistant | xml | off | none | none | none | none | 内置 suite |
| 11 | 自定义 markdown cases | md-fence | off | deep-fence | no-tool | none | none/… | `--cases *.json` |
| 12 | primitive upstream | md-fence(bench) | off | renderer fence | none | submit/— | none | `--suite primitive-*` |
| 13 | primitive go-native | md-fence(bench) | off | renderer fence | none | submit/— | none | `--primitive-profile go-native` |
| 14 | native transport | native | off | none（有 tools 时） | 由 format 决定 | 同上 | 同上 | `chat-completions` |
| 15 | 救援/重复兜底 | 任意 | — | — | — | — | — | loop 轴触发 |

> cell 12/13 的 `prefill` 是**渲染器自带**的围栏（`G1IFunctionRenderer.Render` 末尾），
> 与产品 `fence` 不是同一机制但字节接近；P2 需要决定它算 `prefill=fence` 还是
> `prefill=renderer-fence`。

---

## 4. 跨轴约束表（P2 的校验清单）

| # | 约束 | 现状行为 | 目标行为 |
|---|---|---|---|
| C1 | `thinking ∈ {fast, full}` ⇒ `prefill=none` | 半开/全开占用 opening；XML+router 时 `<tool_call>` 被**静默丢弃**（`protocol_messages.go:81-86` + `prompt_build.go:82`） | 构造期报错，或显式改为「闭合 think + 锚点」的合法组合 |
| C2 | `format=md-fence`（产品）⇒ `thinking=off` | CLI/API 已报错 | 保留 |
| C3 | `prefill=deep-fence` ⇒ `abstain ≠ none` | **无校验**（PREFERENCES 要求成对） | 构造期报错 |
| C4 | `prefill=fake-think-*` ⇒ `thinking=off` 且与 `deep-fence` 互斥 | fake-think **静默覆盖** deep anchor（`runner_turn.go:155,357`），与文档相反 | 构造期报错（或按文档改为锚点优先） |
| C5 | `terminal=submit` ⇒ 目录含 submit 且 `EndOnTerminalTool` | 逐题推导 | Spec 构造时解析 |
| C6 | `tools=progressive` ⇔ `route=progressive` | 同一开关，无独立校验 | 合并或显式约束 |
| C7 | `format=native` ⇒ `transport=native`；native 且有 tools 时 `prefill=none` | 运行时清空 `AssistantPrefix`（`native_tools.go:116-123`） | 构造期表达并记录 |
| C8 | `route ≠ none` ⇒ route renderer thinking off 且 route budget ≤ answer budget | `applyRunnerDefaults` 已校验 | 保留 |

---

## 5. golden 覆盖矩阵

### 5.1 现有（7，必须不变）

| 文件 | 覆盖 |
|---|---|
| `xml_tool_then_final.txt` | XML off，无 router，tool→final |
| `xml_thinking_fast.txt` | XML fast 半开 |
| `xml_thinking_full.txt` | XML full 半开 |
| `xml_answer_stage.txt` | XML answer 阶段 |
| `product_fenced_tool_then_answer.txt` | md 产品浅锚点，3 步 |
| `product_submit_fence_prefix.txt` | md 产品 + submit |
| `functions_benchmark_fence.txt` | md benchmark（HasSubmit/HasRunTests） |

### 5.2 待补（P1 补齐，按轴分组）

**A. 预填 × 格式矩阵（缺口最大）**

- `xml/route-respond-inspect/prefill-envelope`：router 决策 prompt + `<tool_call>` 锚点
- `xml/route-progressive/prefill-envelope`：route prompt + 决策 prompt
- `md/prefill-fence`：浅锚点字节（` ```json\n `）
- `md/prefill-deep-fence`：深锚点字节（`{"name":"`，冒号后**无空格**）
- `md/prefill-fake-think-half` / `-closed`：含自注入前缀的剥离
- `native`：`nativeTracePrompt` 的 JSON + `nativeMessages` 翻译（golden 存 JSON）
- `xml + thinking full + prefill-envelope`：**当前不可达**，P2 决定是否开放

**B. 动作空间**

- `abstain=no-tool`：非空 `answer` 直接 final；空参数 → answer stage
- `abstain=no-tool+gate-state`：拒绝时的 re-ask prompt
- `abstain=no-tool+gate-evidence`：引用证据/不引用的两种结果
- `terminal=submit`：primitive `HasSubmit=true` 与 `false`（裸 `Assistant:`）
- `terminal=submit` + `HasRunTests`：`PASS` 前后渲染器切换

**C. 循环兜底（用户强调依赖循环计数）**

- 重复调用：replay note（streak≤2）与拒绝 note（streak≥3）
- 同工具连续成功：进入 rescue 的 catalog + 指令
- 连续失败 2 次：第三次拒绝 + recovery 文本
- protocol retry：unclosed think / token limit / invalid shape 三种 correction
- answer stage 违规：专用 re-ask
- rescue 模式：仅 terminal tool 的目录 + rescue instruction

**D. 答案阶段与结果渲染**

- answer stage + unverified 列表
- 工具结果压缩（`compress-fetch`）与 `spawn_agents` 块渲染
- catalog 三种渲染：XML 散文 / md 扁平 schema / native schema

**E. BFCL（同 golden 机制，独立目录）**

- markdown anchor `{"name":"` / parallel `[{"name":"`
- xml baseline（fast 半开）与 xml anchor（闭合 think + `<tool_call>{"name":"`）
- multi-turn anchors

### 5.3 golden 机制改造（P1）

把 7 个手写测试函数改成**表驱动**：

```go
for _, cell := range wire.RegisteredSpecs() {
    runScriptedTurn(t, cell.Spec, cell.Outputs)
    compareGolden(t, "testdata/golden_prompt/"+cell.Canonical+".txt", got)
}
```

文件名 = canonical ID；新增轴值必须同时新增 golden，否则测试失败。

---

## 6. 命名、hash 与兼容

- **canonical**：按固定轴序拼接非默认值，例如
  `xml,think-fast,prefill-none,abstain-none,terminal-none,route-none,tools-full,control-base`
- **hash**：canonical JSON 的 sha256；manifest 同时记 `canonical` 与 `hash`
- **preset**：注册表把短名映射到 canonical，例如
  - `xml-v1` → 产品 XML 默认
  - `md-v1` → 产品 Markdown 默认（deep-fence + no-tool）
  - `md-v1+anchor` → 浅锚点
  - `primitive-v1` / `primitive-v1+gonative`
  - `bfcl-md-v1` / `bfcl-xml-v1` / `bfcl-xml-v1+anchor`
- **未注册组合**：默认允许，manifest 标 `registered=false`；`--strict-spec` 下报错
- **旧 manifest 字段**：`protocol/renderer/decision_fake_think/deep_tool_anchor/...` 继续写，由 Spec 派生
- **旧 flag**：保留为长写别名，映射见 §2

---

## 7. P1 验收标准

1. `wire.Spec` + `Normalize/Validate/Canonical/Hash` 落地，所有入口走同一收口。
2. CLI 支持长写轴 flag 与 `--profile` 简写，两者产出同一 canonical/hash。
3. `eval explain <id>` 打印完整 prompt 预览 + stops + budgets + 轴值。
4. 现有 7 个 golden 字节不变；§5.2 的 A/B/C 组 golden 落地。
5. 旧 flag 映射表逐条有单测；未注册组合能跑且被标记。
6. `docs/continuation-and-agent-protocol.md` 的 profile 表改为引用 Spec canonical。

---

## 8. 待确认

1. **候选次轴**（`feedback`、`subagent`）是否纳入 Spec？它们确实改模型看到的字节。
2. ~~`format=native` 建模~~ → **已定：独立 `transport` 轴**（§1.0），理由是 native 只替换调用通道，
   control/answer/tool-result 仍由文本格式决定，且 generator 才探测得到。
3. ~~`loop.SameToolRescueLimit` 默认~~ → **已定（用户 2026-09-08）：统一到产品常量 3**，
   8 保留为显式实验值 `--same-tool-rescue-limit 8`。见 §1.1 的解决说明。
4. ~~primitive 的 renderer 围栏~~ → **已定：`prefill=fence` + `transcript=benchmark`**，
   owner 由 transcript 隐含，不再单独开值。
5. **`xml + thinking full + prefill=envelope`**：P2 是开放为合法组合（BFCL 已验证）还是继续禁止？
   P1 的 Validate 暂时禁止（`thinking != off` 即占用 opening），因为现有 XML renderer 只实现半开。

---

## 9. P1 进度（2026-09-08 本轮）

已落地（`go test ./internal/agent/... ./api/... ./cmd/rwkv-cli/...` 全绿）：

- `internal/agent/wire/spec.go`：12 轴枚举 + `Spec` + `Normalize/Validate/Canonical/Hash/Short`；
  §4 的 C1–C7 全部变成带稳定错误码的 `SpecError`。
- `internal/agent/wire/registry.go`：preset 注册表（`xml-v1`/`md-v1`/`primitive-v1`/`bfcl-md-v1`/
  `bfcl-xml-v1`/`native-v1` 等）+ 自由组合修饰符（`+anchor`/`+fence`/`+no-tool`/`+gate-state`/
  `+fake-think`/`+progressive`/`+think-fast`…）+ canonical 解析。`Resolve` 接受
  preset 名、`preset+modifiers`、canonical 三种写法。
- `internal/agent/wire_legacy.go`：`WireSpecOf(Options)`（旧字段 → Spec）与
  `OptionsWithWire(base, Spec)`（Spec → 运行时字段）双向映射；`Options.Wire` 作为门面字段。
- 测试：10 个可达 cell 全部通过「构造 → 描述 → 应用 → 再描述」的往返一致性；
  两个静默冲突（XML+thinking+router、deep-fence 无 abstain）现在返回 `SpecError`，
  同时仍返回 Spec 供 manifest 记录非法组合；`md + fake-think + deep-anchor` 的
  fake-think 优先级被固定为测试断言。

下一步（P1 剩余）：CLI 长写轴 flag + `--profile` 简写 + `eval explain`；
表驱动 golden（§5.2 A/B/C 组）；manifest 写 `wire.canonical/hash/axes` 并保留旧字段派生。

### 9.1 本轮追加（P1 第二轮）

- **manifest 可自描述**：`run.json` 的 `manifest.harness` 新增 `wire_canonical`、`wire_hash`、
  `wire_conflict`；`RunSchemaVersion` 6 → 7。旧字段（`protocol`/`renderer`/`deep_tool_anchor`…）
  继续写，由同一份 Options 派生，所以旧分析脚本不受影响。`wire_conflict` 会把
  XML+thinking+router 这类"runner 静默丢锚点"的组合写进产物，而不是报告一个干净配置。
- **CLI 简写入口**：
  - `agent-eval --list-profiles`：列出注册 profile 与修饰符（不需要 `--model`）。
  - `agent-eval --explain-profile <spec>`：打印 preset/canonical/hash/short、protocol/renderer、
    thinking，以及完整 control prompt（不需要 `--model`）。
  - `agent-eval --profile <spec>`：在 suite 默认 Options 之上应用 Spec；与
    `--agent-protocol`/`--thinking`/`--semantic-no-tool`/`--deep-tool-anchor`/`--route-stage` 等
    单轴开关同时出现时**报错**，避免 flag 顺序决定语义。primitive suite 暂不接受 `--profile`
    （P4 把逐题 protocol/renderer 移进 suite spec）。
  - `agent --profile <spec>`：经 `api.Config.Profile` 进入 `sessionRunnerOptions`，在
    product/XML 构造器之上应用；`applyProtocolDefaults` 在有 profile 时跳过逐协议归一化，
    `decisionMaxTokens` 保持 0 由 `NewRunner` 按 profile 的实际 format 取默认（避免
    XML 的 512 泄漏到 markdown profile）。
- **测试**：CLI 解析/冲突/查询路径（`cmd/rwkv-cli/main_test.go`）、API 覆盖
  （`api/service_test.go`）、manifest 记录与冲突可见性（`internal/agent/eval/runner_test.go`）。

下一步（P1 剩余）：表驱动 golden（§5.2 A/B/C 组，文件名 = canonical ID）；
旧单轴 flag → 轴长写别名（保持兼容）；`--strict-spec` 与匿名组合标记。

### 9.2 本轮追加（P1 第三轮）

- **表驱动 golden 落地**：新增 `internal/agent/wire_golden_test.go` + `testdata/golden_prompt/wire/`
  10 个 cell，覆盖 §5.2 的 A/B/C 组：
  - A 预填：`product_md_deep_anchor`（产品实际默认，此前无字节锁）、
    `product_md_fake_think_half`、`product_md_fake_think_closed`、
    `xml_route_envelope`、`xml_progressive_route`；
  - B 动作空间：`product_md_no_tool_answer`、`product_md_no_tool_empty_to_answer_stage`、
    `product_md_gate_state_reject`；
  - C 循环兜底：`product_md_rescue_same_tool`（同工具 spiral → submit-only rescue）、
    `xml_protocol_retry_unclosed_think`。
  原 7 个手写 fixture 未改动，仍是历史基线。
- **golden 顺带固化的一条行为**：被 no_tool gate 拒绝后，deep anchor 仍然保持武装，
  下一次决策依旧是调用续写；只有真正执行的调用才会清掉前缀（见
  `product_md_gate_state_reject.txt`）。这条此前没有字节测试。
- **`loop.SameToolRescueLimit` 统一为 3**：`--same-tool-rescue-limit` 默认改为
  `agent.ProductSameToolRescueLimit`；bfcl-product 的显式重置保留为防御性不变量；
  历史值 8 只能显式传入。`bfcl-multiturn` 的 12 属于另一 harness，不在统一范围。

下一步（P1 剩余）：旧单轴 flag → 轴长写别名（保持兼容）；`--strict-spec` 与匿名组合标记；
native transport 的 golden（需要 fake `toolchat.Completer`）。

### 9.3 本轮追加（P2：预填收敛 + 构造期校验）

- **单一预填所有者**：新增 `wire.Spec.DecisionFrame(DecisionState)`（`internal/agent/wire/frame.go`）。
  决策阶段的 assistant opening 只由它决定，规则按优先级：
  1. respond 路由 / answer 阶段不预填；
  2. `transcript=benchmark` 由 renderer 自带围栏，frame 返回空（避免双重围栏）；
  3. `fake-think-*` 在**每个** decision 步都武装（它是唯一替换锚点而非叠加的机制）；
  4. 格式锚点（envelope/fence/deep-fence）在首次决策武装，工具步之后仅当 terminal tool
     未完成时重新武装。
- **8 处赋值点 → 4 处**，且剩下的 4 处都不是"格式选择"：`prepareAnswerStage`（协议持有的
  answer 前缀）、`resolveFrame`（唯一决策所有者）、`acceptSemanticNoTool` / answer 阶段
  re-ask 的 `Assistant:`。`initialize`、`runToolAction` 清空、`advanceAfterTool` 重装、
  `resolveDecisionPrefix` 全部删除。`ActionProtocol.ToolCallPrefix()` 从接口移除，具体方法
  改为委托 wire 常量，字节单一来源。
- **构造期校验**：`NewRunner` 现在会 `WireSpecOf(options)` 并拒绝 spec 不成立的组合
  （例如 deep anchor 没有 abstention 出口）。这是 P2 的行为变化：以前静默跑，现在报
  `prefill.requires-abstain`。
- **派生修正**：XML + thinking + router 不再派生为冲突——renderer 在 think 块占用 opening 时
  本来就拒绝注入前缀，所以 `WireSpecOf` 现在如实派生 `prefill=none`。`terminal` 轴放宽为
  任意合法工具名（测试用 `echo` 作为 terminal），`submit` 只是 benchmark 的名字。
- **回归锁**：新增 golden `xml_route_answer_stage`（router 的 envelope frame 在 answer 阶段必须
  让位，输出以 `Assistant: <answer>` 重建）——这正是重构中差点引入的 stale-frame bug。
  golden 矩阵 11 个新 fixture + 原 7 个全部逐字节不变；`wire/frame_test.go` 锁 frame 规则表；
  `TestNewRunnerRejectsInvalidWireSpec` 锁构造期拒绝。

下一步（P2 剩余 → P3）：`--strict-spec` / 匿名组合标记；旧单轴 flag 的轴长写别名；
native transport golden；然后进入解析 codec 收敛（容错阶段带 ID 进 trace/manifest）。

### 9.4 本轮追加（P3：解析容错可观测）

- **修复阶段 ID 化**：新增 `internal/agent/wire/repair.go`，14 个稳定 ID
  （`think_stripped`、`array_envelope`、`envelope_recovered`、`json_repaired`、
  `function_wrapper`、`key_alias`、`arguments_hoisted`、`stringified_arguments`、
  `nested_name`、`name_inferred`、`tool_renamed`、`path_argument`、`legacy_xml_call`、
  `xml_path_alias`）。两个 parser 的每个容错分支现在都记录自己修了什么，
  不再是单一 `ProtocolRepaired` 布尔。
- **链路**：`Action.Repairs` → `Step.ProtocolRepairs` → `summary.metrics.repairs_by_id`。
  于是"prompt 改动把工作悄悄推给 parser"会表现为 repair 计数结构变化，而不是分数不动。
- **声明式恢复词汇表**：`Spec.ParseRepairs()` 按 format 声明允许的恢复阶段
  （XML 额外继承 fenced 的全部阶段，因为 `<tool_calls>` 会委派过去），
  `Spec.AllowsRepair()` 供校验；测试断言 parser 实际发出的 ID 必须落在词汇表内。
  `--explain-profile` 现在也打印这行。
- **行为不变**：全部既有 parser 测试（`g1i_functions_test.go` / `protocol_test.go`）与
  18 个 golden 逐字节通过；顺带修掉一个潜在缺陷——原 `inferG1IToolName` 失败时会用
  `protocolRepaired = call.Name != ""` 把先前的修复标记清掉，现在由日志持有，不会被覆盖。
- **结构性合并推迟到 P5**：两个 parser 之间剩下的重复主要是"信封提取"的少量分支，
  而真正的大重复在 `internal/bfcl` 的 `ParseXMLCalls` / markdown parser——那属于 P5 的范围。

下一步：P4（`SuiteSpec` 收敛 + manifest 逐题生效值），顺带补 P2 尾巴
（`--strict-spec` / 匿名组合标记、旧单轴 flag 长写别名、native golden）。

### 9.5 本轮追加（P4：eval 配置收敛 + manifest 逐题生效值）

- **单一解析器**：新增 `internal/agent/eval/suite.go` 的 `SuiteSpec` / `SuiteFor` 与
  `resolveCaseOptions(config, case)`。`Run`、`runCase`、`runManifest` 现在都调用它，
  于是"suite 级归一化 + 逐题覆盖"两层合并成一层：
  - `Run` 不再改写 `config.Runner`（primitive 的 protocol/renderer/terminal/decision budget
    全部下沉到逐题解析）；
  - `runCase` 不再自己拼 primitive 覆盖；
  - primitive 的 `MaxSteps` 逐题取 `max_turns`，`DecisionMaxOutputTokens` 逐题取答案预算。
- **manifest 记录逐题生效值**：`RunSchemaVersion` 7 → 8，新增 `manifest.case_wires[]`
  （`id` / `wire_canonical` / `wire_hash` / `wire_conflict` / `terminal_tool` / `max_steps` /
  `decision_max_output_tokens`）。这修掉了"run.json 说 terminal_tool=submit，但 001 arithmetic
  实际没有 submit"的失真。
- **suite 级字段保留为聚合摘要**（兼容旧读者）：逐题一致时取该值；不一致时回落到 base
  （混合 primitive suite 的 `terminal_tool` 现在是空而不是误导性的 `submit`）；
  `max_steps` 取逐题最大值。原有 `TestPrimitiveSuiteUsesCaseMaxTurns` 等断言不变。
- **CLI 去重**：`agentRunnerOptions` 里 3 份 product 字面量合并为 `productRunnerOptions`，
  4 份 `continuation.Request` 字面量合并为 `evalGenerationRequest`；字段值逐一保持原样。

下一步：P5（BFCL 合流：`internal/bfcl` 复用 wire codec/anchor），以及 P2 尾巴
（`--strict-spec` / 匿名组合标记、旧单轴 flag 长写别名、native golden）。

### 9.6 本轮追加（P5：BFCL 与 wire 合流）

- **帧处理单一来源**：新增 `internal/agent/wire/framing.go`
  - `StripLeadingThinkBlocks`（原来 agent 与 bfcl 各有一份正则 + 各写一遍调用）；
  - `TrimWithheldOpening`（网关保留的闭合 `>`，仅当后面是工具信封时剥离）。
  agent 的 3 处（XML 决策解析、两条 route 解析）与 bfcl 的 `ParseXMLCalls` 现在都调用同一份。
- **锚点字节单一来源**：`wire` 新增/复用 `EnvelopePrefix`、`EnvelopeClose`、`FencePrefix`、
  `CallBodyAnchor`（`{"name":"`）、`ArrayCallAnchor`（`[{"name":"`），
  `DeepFencePrefix = FencePrefix + CallBodyAnchor`（常量拼接，保证一致）。
  BFCL 的 `XMLAnchor`、`xmlClosedThinkPrefix`、`MultiTurnAnchor.Prefill()`、
  `prefillAnchor()`、`assembleMarkdownContent` / `assembleMultiTurnContent` 全部改为读 wire 常量；
  agent 的 `G1IDeepToolAnchorSuffix` 同样是 wire 的别名。
- **有意保留的差异**：BFCL 的 `ParseXMLCalls` 仍保留自己的**多信封扫描循环**——产品 parser 的契约
  是"恰好一个调用"，BFCL 的 parallel split 需要在一次响应里收集多个 `<tool_call>`。
  合流的是"帧与字节"，不是"单调用契约"；这一点在 `xml.go` 的注释里写明了。
- **测试**：`wire/framing_test.go` 锁两条帧规则；`bfcl/wire_anchor_test.go` 锁
  "BFCL 的锚点 == wire 常量"；既有 bfcl prompt/parse 测试（含 prompt SHA 断言）全部不变。

> 环境备注：`go test ./internal/...` 会包含 `internal/tui/concurrent` 的 PTY 测试，
> 它们在本沙箱下因 `operation not permitted`（无法分配 pty）失败，与本次改动无关；
> 改动覆盖的 `internal/agent/...`、`internal/bfcl`、`api`、`cmd/rwkv-cli` 全绿。

下一步：P6（文档生成：profile 表 / 轴表 / 恢复词汇表从代码生成），以及 P2 尾巴
（长写轴 flag 让 think × 工具格式自由组合、`--strict-spec`、native golden）。

### 9.7 本轮追加（P2 尾巴：长写轴 override）

- **`--wire` 长写入口**：`wire.ParseOverrides` / `Spec.WithOverrides`
  （`internal/agent/wire/override.go`）接受 `key=value` 列表，键就是 canonical 的轴名
  （format/thinking/prefill/abstain/terminal/route/catalog/control/feedback/subagent），
  在 **suite 默认或 `--profile` 之上**只改被点名的轴。这样"think 模式 × 工具格式"的任意组合
  不再需要先注册 preset：
  ```sh
  agent-eval --suite bfcl-product --wire "format=md-fence,prefill=fence,abstain=no-tool"
  agent-eval --suite bfcl-product --profile xml-v1 --wire "thinking=fast"
  agent-eval --explain-profile xml-v1 --wire "route=respond-inspect,prefill=envelope"
  ```
  最后一个会先打印解析后的 canonical/hash/control prompt；把 `prefill` 换成 `envelope` 而
  `thinking=full` 会直接报 `prefill.conflict`（见下）。
- **校验与冲突**：`--wire` 与旧单轴开关（`--deep-tool-anchor`、`--semantic-no-tool`…）互斥
  （同一轴两个来源会让语义依赖 flag 顺序）；未知键/重复键/空值在 parse 阶段报错；
  最终 spec 仍走 `Validate`，跨轴冲突照常拒绝。primitive suite 暂不接受 `--profile`/`--wire`
  （suite 仍钉住逐题 transcript）。
- **API 侧**：`api.Config.Wire` 与 `Profile` 同路径，在 `sessionRunnerOptions` 里叠加；
  `applyProtocolDefaults` 在二者任一存在时跳过逐协议归一化并校验 override 串。
- **测试**：`wire/override_test.go`（parse/组合/冲突）、`cmd/rwkv-cli/main_test.go`
  `TestWireLonghandOverrides`（长写、preset+长写、互斥、primitive 守卫、API 透传）、
  `api/service_test.go` `TestWireOverridesComposeOnProtocolDefaults`。

剩余：P6（文档生成）；`--strict-spec` 与匿名组合标记；native transport golden。

### 9.8 本轮追加（P6：文档生成）

- `wire.DocsMarkdown()` 从注册表与枚举渲染三张表：registered presets（name / canonical / short）、
  axis domain（每个轴的合法值）、recovery vocabulary（每种 transcript 允许的修复 ID）、
  修饰符与 override key 列表。
- 检查进仓库的产物是 `docs/refactor/wire-profiles.md`；`TestDocsAreGenerated` 逐字节比较，
  `go test ./internal/agent/wire -update-wire-docs` 重写。于是新增 preset / 轴值 / 修复 ID
  而不更新文档会直接测试失败。
- 这也是 P6 的落地方式：不引入单独的生成脚本，用测试把"文档 == 代码"变成可执行契约。

剩余（收尾）：`--strict-spec` 与匿名组合标记（未注册组合默认允许、manifest 标 registered=false，
`--strict-spec` 下拒绝）；native transport 的 golden（需要 fake `toolchat.Completer`）。

### 9.9 本轮追加（收尾：匿名可追溯 + native golden）

- **匿名组合可追溯**：`Spec.MatchPreset()` 按轴（忽略 loop）匹配注册 preset，
  `default`/`xml-v1` 这类同轴别名优先返回非 `default` 的名字。`run.json` 的
  `harness.wire_preset` 与 `case_wires[].wire_preset` 记录命中的 preset；为空即匿名组合，
  仍由 `wire_canonical`/`wire_hash` 完整标识。
- **`--strict-spec`**：agent-eval 的纪律开关。未注册组合默认允许（可跑、可追溯），
  加上该 flag 后要求最终 spec 命中注册 preset，否则报错并打印 canonical，
  逼实验先登记为 preset。
- **native transport golden**：`native_tool_then_answer.txt` 锁定原生 Chat Completions 路径
  （文本续写 golden 矩阵覆盖不到）：native 控制指令、message 翻译、工具目录排序、
  `tool_choice` 从 `required`（首次决策）到 `auto`（工具之后）的升级、
  assistant/tool 消息对，以及"提供 tools 时 assistant_prefix 必须为空"。
  测试用只实现 native 的 fake generator，文本路径被调用即失败。
- **最终验证**：原 7 个 golden 未被修改（`git status` 无改动），新增 12 个 wire golden
  （11 文本 + 1 native）全部逐字节通过；`go test ./internal/agent/... ./internal/bfcl/
  ./api/... ./cmd/rwkv-cli/...` 全绿；`go vet`、`gofmt` 干净。

至此 P0–P6 全部落地，目标收口。










