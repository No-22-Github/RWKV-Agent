# 续写接口与 Agent 协议边界

状态：实验性 v1

## 1. 原则

RWKV 的基础能力是“给定完整文本前缀，继续生成文本”。HTTP 服务、对话模板和工具动作
不是同一层能力，因此项目将它们拆开：

```text
Agent Runner
  ├── ActionProtocol：动作说明、输出解析、协议纠错
  ├── PromptRenderer：结构化 transcript -> 完整文本前缀
  └── continuation.Generator
        ├── 本地 inference.Session adapter
        ├── rwkv_lightning HTTP adapter
        └── Chat Completions adapter（可选 chatcompletions build tag）
```

`continuation.Generator` 只接收 prompt、采样参数、停止串和输出 token 上限，只返回续写
文本。它不知道 system/user/tool role，也不知道 JSON、工具注册表或 OpenAI 协议。

## 2. 当前内建协议

协议没有被强行合并成一套字节格式；统一的是产品构造入口和层级边界：

| Profile | 动作协议 / renderer | 用途与终止语义 |
| --- | --- | --- |
| 产品默认 | `rwkv-g1i-envelope-v1` / `rwkv-chat-continuation-v2` | XML 工具信封、普通文本 final；默认无 Router，可使用 off/fast/full thinking |
| Markdown 可选 | `rwkv-g1i-functions-product-v1` / `rwkv-g1i-functions-product-continuation-v1` | `--agent-protocol markdown`；工具后直接输出普通 Markdown，无 `submit` gate |
| Primitive | `rwkv-g1i-functions-v1` / `rwkv-g1i-functions-continuation-v1` | benchmark 专用逐题目录与 `submit` 终止，不代表产品默认 |
| BFCL wrapped | `internal/bfcl` 的对象/数组 anchor 与 strict/wire-compat parser | BFCL 官方/诊断评测专用，不进入 Agent 产品 prompt |
| 原生 function calling | Chat Completions `tools/tool_calls` | Provider 外层结构化调用；不伪造 `no_tool` 等 API tool |

两个面向调用方的 profile 各有唯一构造入口，都在 `internal/agent/harness_profile.go`：

| 构造器 | 使用方 |
| --- | --- |
| `agent.XMLHarnessOptions` | App、`rwkv-cli agent`（默认 XML）及 XML 产品评测 |
| `agent.ProductHarnessOptions` | 显式 `--agent-protocol markdown` 与冻结的 `bfcl-product` Markdown 基线 |

调用方不再手写 `agent.Options` 字面量，protocol/renderer 配对、progressive Router 接线和
循环策略都由构造器持有。循环策略常量（`ProductDuplicateReplayLimit` = 2、
`ProductDuplicateRescueThreshold` = 3、`ProductSameToolRescueLimit` = 3）两个 profile 共用：
它描述的是模型的重复调用习惯，不是 transcript 格式的属性，因此没有按 profile 分叉的依据。
`TestHarnessProfilesShareLoopPolicyDefaults` 锁住这一点。

Primitive 与 BFCL wrapped 继续使用各自的独立入口，防止评测协议字节漂移到产品。

协议、renderer 和 route 的 ID 常量集中在 `internal/agent/protocol_core.go` 一个 block 里。
这些字符串逐字节进入 eval manifest，归档 run 只有在拼写不变时才可比，因此新增 profile
应该在该 block 加一行，而不是在 `ID()` 方法里内联字面量。

可选 Markdown profile 复用 G1i checkpoint 的训练 transcript：

````text
System: Tools:
[{"name":"read_file",...}]

User: Read README.md.

Assistant: ```json
{"name":"read_file","arguments":{"path":"README.md"}}
```

User: Function output:
1: # RWKV-Agent

Assistant: RWKV-Agent
````

Router 明确选择 `inspect` 后，第一次工具选择在 `Assistant:` 后预填 JSON code fence，模型只需
续写调用对象。工具结果之后回到未锚定的 `Assistant:`：模型可以为具体缺失事实再输出一个
fenced JSON 调用，也可以直接返回包含代码块的普通 Markdown。`respond` 路由同样不预填工具
格式并直接回答。产品不注册 `submit`，最终答案不需要放进 JSON 字符串。解析器继续容忍 raw
JSON、字符串化参数、截断 JSON、字段别名和旧 XML 包装，但普通 fenced Markdown 不会被误
执行为工具；修复行为仍在 trace 中保留原始失败分类。

成功执行一个工具后保留 assistant/tool 消息对，并让模型选择继续调用另一个不同工具或
直接回答。训练原生 transcript 不额外注入通用 Agent reminder；失败、重复调用和 rescue
提示合并进同一个 `Function output` 回合。`read_file` 路径失败时仍由 Controller 引导模型用
`list_files` 或 `search_text` 发现真实路径。
同一精确调用无论成功或失败都只允许出现一次；同一工具实际执行连续失败两次后，第三次
调用会被拒绝，直到模型改用不同工具或直接说明限制。

重复调用达到阈值后，Runner 禁用其他工具并要求模型用已有证据直接给出最佳答案。工具全部
失败或证据不足时，答案必须明确说明限制。过长字符串保留开头和与任务词项最相关的窗口，
单个字符串最多约 2400 Unicode 字符。

`rwkv-g1i-envelope-v1` 与 `rwkv-chat-continuation-v2` 是产品默认 XML profile。它在三个
方面结构性优于 fenced JSON：

- **闭合更积极。** `RWKV-Toolcall-Bench` 给定框架开头后的闭合率：`<tool_call>` 20/20
  (13.3b) 与 15/20 (7.2b)，fenced JSON 为 16/20 与 10/20。
- **参数更完整。** `rwkv-abstention-lab` 无预填时 required-complete 94%（XML）对
  68%（markdown）；配合 fast-think 为 100% 对 98%。
- **终止符不与内容冲突。** 产品 profile 在决策回合把 ` ``` ` 作为停止串，因此参数中
  含围栏的调用（例如写入带代码块的 Markdown）会被从中间截断；XML 停在 `</tool_call>`，
  该终止符不会与工具参数内容碰撞。当前只读产品工具集触发不到这一点，但它是协议层
  的边界，选型时应计入。

两个 profile 都实现 `no_tool` 语义弃权，各自用自己的信封表达：产品用 fenced JSON，
XML 用 `<tool_call>{"name":"no_tool","arguments":{"reason":"..."}}</tool_call>`。参数校验
与 Runner 语义完全共用——不查执行表、不执行工具、`toolExecuted`/`toolEvidence` 恒为
false、未知字段 fail closed。因此 `--suite bfcl-product` 接受两种 profile，可以在同一批
题上直接对照；benchmark profile（Primitive、BFCL wrapped）仍被拒绝，因为终止语义不同。

选择由 `--agent-protocol xml|markdown` 控制，产品入口默认 `xml`。默认同时关闭 progressive
Router，模型直接看到完整的已启用工具目录，并在一个阶段里选择普通文本 final 或完整
`<tool_call>{JSON}</tool_call>`。XML 下 `deepToolAnchor` 与 `semanticNoTool` 默认关闭：前者没有
JSON 围栏可延长，后者会增加目录长度但模型本来就能直接回答。`decisionFakeThink` 仍然报错，
因为 XML renderer 由 `--thinking` 预填自己的 think 块；XML 上应直接用
`--thinking fast/full`。

Primitive Bench 继续使用独立的 `rwkv-g1i-functions-v1` 与 benchmark `submit` 终止语义。

动作协议、prompt 渲染器和续写 adapter 独立版本化。父 Agent 内仍是顺序多工具状态机；
`spawn_agents` 可以批量并发运行多个相互独立的子状态机，但显式 planner、子任务依赖图和
递归委派仍不属于 v1。

### 2.1 模型偏好实验开关

两个开关默认关闭，并只改变产品文本续写 profile：

- `semanticNoTool` / `--semantic-no-tool`：在文本工具目录中加入协议伪动作 `no_tool`。只接受
  精确名称；参数只能为空对象，或包含可选字符串 `reason` / `answer`，未知字段与非字符串值
  继续 fail closed。非空 `answer` 优先、否则 `reason` 直接作为本轮用户可见 final；Runner
  不查执行表、不执行工具、不生成假的 Function output 或 evidence。原始动作、解释字段和
  parser repair 仍写入 Step/trace，App 以“无需工具”事件显示。只有空参数保留为切到
  `StageAnswer` 再生成普通文本的兼容路径。评测 outcome 单独记为 `semantic_no_call`。
- `decisionFakeThink` / `--decision-fake-think`：只在 `StageDecision + inspect + 当前没有其他
  assistant prefix` 时，把 prompt 精确结束为 `Assistant: <think></think`。末尾 `>` 由模型
  续写；Harness 在解析前移除自己注入并由模型闭合的前缀，因此不会伪记 parser repair。
  `closedFakeThink` / `--closed-fake-think` 改填完整的 `<think></think>`。半开不是笔误：
  实测该 tokenizer 上 `>` 与 `>{` 都是 1 个 token（后者合并），留着 `>` 让模型能一步进入
  结构化输出。**两者在 60 题上均已被否定**（各 17/60，低于不干预），因为它们都必须关掉
  `deepToolAnchor`，而撤掉围栏会让模型漂移到 XML 信封。压制思考把误调用从 1/20 推到
  19–20/20；正确方向是给足决策预算让模型想完，见下条。

- `deepToolAnchor` / `--deep-tool-anchor`：把产品决策锚点从裸 fence ` ```json\n` 延长为
  ` ```json\n{"name":"`。2026-08-28 在 7B 实测（greedy，n=25/cell）：浅锚点把整个
  `arguments` 形状交还给模型习惯，约 50% 输出成 `"arguments":"{\"k\":\"v\"}"` 字符串化
  形态（正是指令里两句话明确禁止的形状，靠 parser 容错兜住）；深锚点下字符串化归零。
  紧凑拼写（冒号后无空格）必须与 `Instructions` 里的 JSON 示例一致，lab 实测一个空格
  会让正样本从 198/200 掉到 38/200。深锚点同时移除全部句法弃权出口，因此只能与
  `semanticNoTool` 一起评估，不能单独开启。锚点深度不改变协议 ID：它是预填字节实验，
  归档 run 仍需跨深度可比。

fake-think 不用于 answer stage、`respond` 路由、已有 fence/object/array anchor 或原生 function
calling。因此 `deepToolAnchor` 开启时 fake-think 自动让位 —— 锚点已占据 assistant prefix
位置，两个开关可以共存而互不干扰。`no_tool` 也不注册为原生 API tool。启用任一开关而 Provider 实际走 native tool
calling 时，Runner 明确拒绝配置，避免静默改变实验含义。精确空格、换行和半开字节是实验
变量，不能“格式化”为更自然的形式。

`reason` / `answer` 是模型生成的用户沟通文字，不是外部事实来源：它们可以进入最终回复和
UI，但不能让 `toolExecuted` / `toolEvidence` 变成 true。若 answer stage 中的 `no_tool` 因
阶段契约被拒绝，UI 仍保留其解释供审计，并明确标为未接受，不能伪装成成功 abstention。

Markdown profile 固定使用 thinking off。默认 XML profile 支持 `--thinking fast/full`；
Markdown 上的半开 think 字节实验使用独立的 `decisionFakeThink` 开关，避免参数被静默忽略或
两套 renderer 语义混用。

### 2.1.1 决策预算按 protocol 取默认

`decision_max_output_tokens` 不是全局常量，而是 transcript 的属性：fenced-JSON profile
预填围栏锚点把模型直接推进调用对象，96 token 足够；XML 信封让模型先推理再决定，96 会把
思考截断在句子中间，动作协议随即把它误判为畸形信封。

因此 `NewRunner` 在调用方未指定时按 protocol 选择：markdown `DefaultDecisionMaxOutputTokens`
= 96，XML `DefaultXMLDecisionMaxOutputTokens` = 512。CLI 的 `--decision-max-tokens 0` 与
API 的零值都表示"由 harness 决定"。60 题实测：XML 从 24/60 升到 33/60（`+9/-0`,
`p=0.0039`），markdown 从 24/60 降到 22/60（噪声内），1024 与 512 无差异。

该值仍受 `Generation.MaxOutputTokens` 夹取——默认答案预算 256 时 XML 实际只拿到 256，
要用满 512 需同时提高 `--max-tokens`。

### 2.2 渐进式工具目录

产品 API 默认不安装 Router，完整的已启用工具目录直接交给 XML 动作协议。可选的
`rwkv-g1i-tool-route-v1` 仍按权限和用途把工具分为四个能力组：

| 能力组 | 权限 | 当前工具 |
| --- | --- | --- |
| `workspace` | `workspace_read` | `list_files`、`read_file`、`search_text` |
| `compute` | `compute` | `calculator`、`data_query`、`datetime` |
| `web` | `network_read` | `web_search`、`web_fetch` |
| `delegate` | `delegate` | `spawn_agents` |

显式设置 `progressiveTools=true` 或 `--progressive-tools=true` 后，Router 只看到能力组名称和
一句描述，输出 `<route>respond</route>`、
`<route>inspect:BUNDLE</route>` 或最多两个组的
`<route>inspect:BUNDLE+BUNDLE</route>`。Runner 由此构造本轮活动 ToolSpec 和执行表；隐藏
工具不能绕过活动表执行。控制工具 `load_tools` 始终可见，只允许加载已启用能力组，并且其
结果不算外部证据。关闭 Router 时不会生成 route event，评测的 route 指标没有分母。

### 2.3 Web 和并发子 Agent

Web Provider 接口保持服务商中立。当前 `web_search` 适配 Brave Search，最多返回 10 条
标题、URL、摘要和来源 ID；`web_fetch` 适配 Tavily Extract，一次获取最多 4 个 HTTP(S)
页面，并限制响应体和进入 transcript 的正文长度。Web 工具只有在显式启用且 Brave/Tavily
密钥都存在时注册；状态 API、事件和结果不会返回密钥。

`spawn_agents` 接受 2–8 个独立任务，使用同一个已加载 Service/model 并发创建隔离 Session。
每个子 Agent 有独立的 recurrent State、transcript、步数和超时预算；子 Session 不注册
`delegate`，阻止嵌套委派。结果稳定按输入顺序返回，部分失败不丢弃成功结果，全部失败则
返回工具错误。

这不改变 `continuation.Generator` 的单请求契约。本地 runtime 用 MLX continuous batching
调度多个 Session；RWKV Lightning adapter 在短 `BatchWait` 窗口内把兼容请求聚合到同一个
`contents[]`；Chat Completions adapter 使用普通并发请求。批量是 Provider/runtime 优化，
不是 Agent 协议或核心续写接口的一部分。

这个默认来自同一 60 题产品 suite 的三次复现：XML 无路由 + 512 token 为 33/60、31/60、
33/60；XML 加 Router 为 21/60，Markdown 加 Router 为 24/60。Router 在 irrelevance 题中
把 18/20 判成 `inspect`，覆盖了 XML 模型本来正确的直接回答选择。历史评测仍用 manifest
冻结自己的 route/profile，不随 App 默认自动改变。

协议格式参考并复核了
[`123123213weqw/rwkv-agent`](https://github.com/123123213weqw/rwkv-agent)：
工具调用使用 greedy 解码、opening fence 预填、closing fence stop 和严格结果重建；
产品仅复用工具调用 transcript，不复用 benchmark `submit` 终止语义。
旧 `agent-json-v1` 裸 JSON 协议已经删除，不保留兼容死代码。

## 3. rwkv_lightning 映射

HTTP adapter 面向 `rwkv_lightning` 的原生续写请求：

- 单请求把完整 prompt 放入 `contents`；启用聚合时，一个 HTTP 请求携带多个并发 prompt。
- `max_tokens`、`temperature`、`top_k`、`top_p` 和重复惩罚逐字段映射。
- 默认 `stream: true`（SSE 逐 token），`--api-stream=false` 切换为一次性 JSON 响应。
- 服务端 `choices[0].message.content` 映射为续写文本。
- endpoint 是 CLI 传入的完整 URL，adapter 不拼接固定路径。
- 密码从指定环境变量读取，错误信息会脱敏。
- 部署层认证使用可重复的通用 header/env 映射，不把 Cloudflare Access 写进续写接口。

参考实现：
[`RWKV-Vibe/rwkv_lightning`](https://github.com/RWKV-Vibe/rwkv_lightning)。

## 4. CLI

本地续写仍是默认值：

```sh
./dist/rwkv-cli agent \
  --completion local \
  --model /absolute/path/to/model.pth \
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 并概括项目"
```

远程续写：

```sh
# Only when the server enables a request-body password:
# export RWKV_API_PASSWORD='...'
export RWKV_CF_ACCESS_CLIENT_ID='...'
export RWKV_CF_ACCESS_CLIENT_SECRET='...'

./dist/rwkv-cli agent \
  --completion rwkv-lightning \
  --api-url https://example.com/v1/batch/completions \
  --model rwkv7-13b \
  --api-header-env CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID \
  --api-header-env CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET \
  --subagents \
  --remote-batch-wait 10ms \
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 并概括项目"
```

远程 Agent 的工具仍在本机执行，但完整 prompt 会包含模型请求过的文件片段并发送到远程
endpoint。选择远程续写即代表显式启用这条数据路径。

`rwkv_lightning_cuda` 的 raw continuation 语义由请求体决定：传 `contents` 数组即逐 token
续写，不重新渲染 role 和 think 前缀；传 `messages` 才会套 chat 模板。客户端始终发送
`contents`，因此 `/v1/batch/completions`、`/v1/chat/completions` 和
`/big_batch/completions` 都可用。具体路径取决于部署，可以用 `GET /openapi.json` 枚举。

`stop_tokens` 在 rwkv_lightning 里是 decoded-text 字符串数组（上游示例 `["\nUser:"]`），
不是整数 token ID；发整数会返回 HTTP 500。默认 `--api-stop-tokens text` 把本轮
`Protocol.Stops(stage)` 的序列原样转发给服务端，使生成在 stop 处真正停止，而不是生成到
`max_tokens` 后仅靠客户端 `splitAtStop` 截断。这同时降低延迟和无效算力。`none` 省略字段；
`eos` 或逗号分隔整数列表保留旧的 token ID 形式，仅供接受整数的部署使用。无论哪种模式，
客户端都继续做 decoded-text 收束，因此协议边界不依赖服务端行为。

`--api-stream` 默认 `true`（SSE 逐 token）。实测某部署的 SSE 在一定负载后会退化为
HTTP 200 空响应体，而非流式路径不受影响；评测只需要最终文本，因此在流式通路不稳定的
部署上应使用 `--api-stream=false`，代价是交互式 `agent` 失去 token 级输出。

`/big_batch/completions` 只支持 `temperature`（无 `top_k`/`top_p`/penalty），且单请求串行：
并发第二个请求返回 HTTP 409 `Another big_batch request is already running`。提前关闭 SSE
连接会让该次生成变成孤儿并继续占用槽位，因此必须把流读到 `data: [DONE]`。需要完整采样
参数或并发的场景应使用 `/v1/chat/completions`。

上游 OpenAI-compatible Chat Completions 使用独立的外层 adapter。默认构建不编译或链接
OpenAI SDK；调用该 provider 前需要使用官方 SDK 可选构建：

```sh
go build -tags chatcompletions ./cmd/rwkv-cli
# macOS 完整发行包：./scripts/build-macos.sh --with-chat-completions
```

adapter 调用示例：

```sh
export OPENAI_API_KEY='...'

./dist/rwkv-cli agent-eval \
  --completion chat-completions \
  --api-url https://example.com/v1/chat/completions \
  --model other-model \
  --suite smoke \
  --output runs/chat-other-model-smoke
```

隐藏推理默认开启且与正文共享输出预算的上游需要显式关闭上游思考。例如 DeepSeek
V4-Flash 应增加：

```sh
  --api-url https://api.deepseek.com/v1/chat/completions \
  --model deepseek-v4-flash \
  --chat-thinking disabled \
  --chat-prompt-mode native-chat \
  --chat-token-limit-field max-tokens
```

adapter 使用官方 `github.com/openai/openai-go/v3`，默认采用 `native-chat`，传递真正的
system/user/assistant messages，并通过官方
`tools`、`assistant.tool_calls`、`finish_reason: "tool_calls"`、`role: "tool"` 与
`tool_call_id` 完成工具闭环。工具参数使用 JSON Schema；满足严格子集的工具设置
`strict: true`。Harness 仍保持“一步一个动作”，所以发送 `parallel_tool_calls: false`：
首次 inspect 使用 `tool_choice: "required"`，后续决策使用 `auto`，回答阶段不提供工具。
模型返回的调用 ID、函数名、JSON 对象参数和 finish reason 都会在执行前校验。若上游忽略
`parallel_tool_calls: false` 返回多个合法调用，adapter 只接纳第一个，剩余动作必须由模型
在后续轮次重新请求，因此不会扩大 Harness 的单步执行边界。
具体字段与消息顺序对齐 OpenAI 的 [Function calling guide](https://developers.openai.com/api/docs/guides/function-calling)
和 [Create chat completion reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)。

`wrapped-continuation` 保留为兼容回退：它把渲染完成的 continuation prompt 放进 user
message，并继续使用 `rwkv-g1i-envelope-v1` 文本控制帧，不发送上游 native tools。两种
模式都固定 `stream: false`；`top_k` 和 `penalty_decay` 没有标准 Chat Completions 字段，
因此不发送并记录为 unsupported sampling。默认输出预算字段是官方推荐的
`max_completion_tokens`；只接受弃用字段的兼容服务可显式设置
`--chat-token-limit-field max-tokens`。评测 manifest 记录 prompt transport、输出预算字段和
上游 thinking 配置。`native-chat` 当前只支持内部 `--thinking off`。

`--chat-thinking` 的默认值是 `auto`，此时不发送厂商扩展，维持通用 Chat Completions
兼容性。`disabled`/`enabled` 分别发送 `thinking.type=disabled/enabled`，仅用于支持该字段的
上游。它独立于控制内部 prompt 和协议的 `--thinking off|fast|full`。评测 manifest 会记录
最终选择的 `upstream_thinking`，便于区分模型行为与 adapter 配置。
思考模式返回的 `reasoning_content` 会与 assistant tool call 一起保留，并在匹配的 tool
result 后回传；DeepSeek thinking mode 不支持 `tool_choice: "required"`，因此仅该组合会在
adapter wire 层降为 `auto`。

## 5. 后续对外兼容层

上游 Chat Completions adapter 已经可以让本项目调用其他模型，但它不等于对外暴露
OpenAI-compatible server。若要让第三方框架调用本地 RWKV-Agent，可在 API 层增加双向翻译器：

1. OpenAI messages/tools 转换为内部 transcript 和 `ToolSpec`。
2. 内建 `Action` 转换为 OpenAI tool call 或 assistant message。
3. OpenAI tool result 转换为内部工具结果记录。

该翻译器消费稳定的内建协议，但不会改变本地工具执行、权限判定或底层续写 adapter。

## 6. 协议评测

2026-07-30 使用 `rwkv-g1i-13b-4922` 远程续写做了三条 smoke test：

- 无工具算术直接回答；
- `read_file` 读取 README 首标题后独立回答；
- `search_text` 定位协议标识后独立回答。

三条均在 greedy 配置下完成，未触发协议重试。这个结果只证明纵向链路，不代表完整
Agent 能力达标。

随后增加了两条回归：直接询问“你有哪些工具”，以及读取并总结包含协议标签的本文档。
两条均可正常完成。由于当前远程服务把输出预算耗尽也报告为通用 `stop`，无法仅靠
`finish_reason` 识别语义截断；Agent CLI 因此把工具选择限制为 256 token，同时把最终
回答预算提高到 1024 token。API 层后续应透出精确 stopping word 和 usage。

同日 18 题 `boundary` 基线在第一次成功工具后立即回答，结果为 4/18；完全开放连续工具
调用后升至 10/18，必需调用从 15/23 升至 21/23，但工具调用从 26 增至 65、工具错误从
9 增至 32，8 个失败 case 都在耗尽 step 后没有答案。`rwkv-agent-eval-v4` 的混合状态机
实测仍为 10/18，必需调用保持 21/23，但工具调用降至 54、错误降至 23，只有 1 个 case
仍因没有任何成功工具结果而耗尽 step。`pb_csv_sum` 恢复，`pb_markdown_release_notes`
则因正确 flag 外附带解释而未通过严格字符串判分；v4 改善了收束，但没有抬高本轮总分。

`rwkv-agent-eval-v5` 在 v4 上加入了 `inspect` 首次 `<tool_call>` 预填、失败恢复提示、
连续失败阻断，以及“任何工具尝试都保留最后回答 step”的规则。summary 新增实际工具执行、
Controller 拒绝、重复调用、连续失败阻断和强制回答计数。同一 13B `boundary` suite 实测
仍为 10/18，失败 case 集合不变；答案分项由 10/18 升至 11/18，必需工具和调用分别由
20/22、21/23 升至 21/22、22/23，工具请求由 54 降至 50，错误由 23 降至 15，唯一的
step 超限空答案降至 0。38 次工具实际执行之外有 12 次重复调用被拒绝，14 个 turn 强制
回答；连续失败阻断为 0，说明本轮错误轨迹先命中了精确重复保护或切换了工具。v5 改善了
失败收束和调用效率，但没有提高端到端通过率。

v5 `smoke` 的严格工具序列评分为 4/10，但 11/11 回答、route 和协议动作均正确；失败来自
证据充分后的额外探索。早期 10/10 smoke 使用“一次成功工具后立即回答”的状态机，不能和
当前顺序多工具循环直接比较。

`rwkv-agent-eval-v6` 将工具参数校验错误与实际工作区观察分开：错误提示携带工具的
精确参数形状，修正参数不会被同工具运行时失败预算提前阻断。若 `inspect` 轮在收束或输出
final 前仍没有任何可信工具观察，Runner 返回 `ErrNoWorkspaceEvidence` 并保持 transcript
不变，防止未验证猜测被后续 Router 当作已提交对话依据。v6 的真实模型基线待重新评测。

`rwkv-agent-eval-v7` 提供默认关闭的 `--few-shot` profile，在初始控制 prompt、成功工具
结果后的近距离提醒和强制回答 prompt 中加入完整轨迹或格式示例。13B A/B 显示 smoke
严格通过从 4/10 升至 5/10，工具请求从 21 降至 16；但 boundary 从 10/18 降至 7/18，
并出现复制示例路径和值的 prompt anchoring。因此该 profile 只用于复现实验，不进入默认
Agent 行为；后续若继续尝试，应避免包含可复制的静态事实，并优先测试抽象或动态示例。

当前 Agent 解码参数为 `temperature=1`、`top_k=1`、`top_p=1`、
`alpha_presence=0`、`alpha_frequency=0`、`alpha_decay=1`。在
`rwkv_lightning` 中 `top_k=1` 会直接选择 argmax，因此 temperature/top-p 实际不参与
采样；两个重复惩罚为 0 时 decay 也不应保留为 0.99。工具协议更依赖稳定的标签和 JSON，
暂不引入会改变 token 排序的重复惩罚。

后续固定同一批中英文任务，对 3B、7B 和 13B 分别记录：

- 首次动作合法率和纠错后合法率。
- 单工具、多工具、错误参数和越权请求的完成率。
- 平均 step、协议重试率、输入/输出 token 和耗时。
- envelope/JSON 被截断、混入思考文本或错误复述工具结果的具体样本。

基准优先复用
[`marty1885/primitive-bench`](https://github.com/marty1885/primitive-bench) 的 30 个
文件型任务、隔离环境、required/forbidden tool 和精确评分规则。它的 G1I completion
runner 同样使用 greedy 解码，并把工具触发与 schema 约束的 JSON 参数生成拆开。接入时
应适配本项目的 `continuation.Generator`，不把 OpenAI 兼容层下沉到底层续写接口。
