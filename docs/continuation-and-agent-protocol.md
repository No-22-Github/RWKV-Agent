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

当前默认动作协议标识为 `rwkv-g1i-envelope-v1`。模型每次生成有两个合法选择：

1. 直接输出普通文本，作为最终回答；
2. 需要仓库证据时，输出 G1I 工具控制帧：

```text
<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>
```

```text
Tool: <tool_result>{"ok":true,...}</tool_result>
```

只有响应从 `<tool_call>` 开始时，本地 `ActionProtocol` 才严格检查完整 envelope 和内部
JSON；其他非空文本直接完成当前任务。这样普通回答不是协议错误，也不会把正文中讨论的
`<tool_call>` 字样误执行为工具。解析器只允许移除开头完整的 `<think>...</think>` 块，
畸形工具控制帧提供一次有界纠错。

prompt 渲染器标识为 `rwkv-chat-continuation-v1`，使用 `System:`、`User:`、
`Assistant:` 和 G1I 的 `Tool:` role。工具选择阶段给出工具 schema 和少量已验证示例；
Router 明确选择 `inspect` 后，第一次工具选择在 `Assistant:` 后预填 `<tool_call>`，
模型只续写 JSON 和 closing tag；Runner 重建完整 envelope 后再交给同一个严格解析器。
没有 Router 的兼容调用路径不做此前缀约束，普通 `respond` 路由也绝不会预填工具标签。

成功执行一个工具后保留 assistant/tool 消息对，并让模型选择继续调用另一个不同工具或
直接回答。每个成功结果后追加收束提醒：证据充分就回答，只为明确缺失的事实继续调用，
且不能重复成功调用。失败结果同样进入 transcript，并给出由 Controller 生成的确定性恢复
提示；`read_file` 路径失败时优先引导模型用 `list_files` 或 `search_text` 发现真实路径。
同一精确调用无论成功或失败都只允许出现一次；同一工具实际执行连续失败两次后，第三次
调用会被拒绝，直到模型改用不同工具或直接回答。

只要本轮发生过工具尝试，Runner 都会把最后一个 Agent step 保留给独立回答阶段；再次
生成同一精确调用会提前切换到该阶段。回答 prompt 替换工具说明、保留此前全部 bounded
assistant/tool 轨迹、禁用工具并预填 `<answer>`；工具全部失败或证据不足时，回答必须
明确说明限制。工具选择阶段只使用 `</tool_call>` stop，回答阶段只使用 `</answer>` stop，
所以总结协议文档时出现工具标签不会被错误截停。过长字符串保留开头和与任务词项最相关
的窗口，单个字符串最多约 2400 Unicode 字符。

动作协议、prompt 渲染器和续写 adapter 独立版本化。当前支持顺序多工具调用；并行调用、
显式 planner 和跨工具依赖图仍不属于 v1。

这个混合状态机来自两层验证：

- OpenAI Agents、Claude tool loop、LangGraph 和 AI SDK 都把“没有工具调用的文本”视为
  最终回答，只在出现结构化工具动作时进入 Tool 节点。
- 当前 G1I 13B 在工具结果后自由选择时会出现“思考决定回答、实际却重复工具调用”的
  解码偏置，因此 v1 同时允许补充证据，并用重复调用保护和末步回答阶段保证有界收束。

协议格式参考并复核了
[`123123213weqw/rwkv-agent`](https://github.com/123123213weqw/rwkv-agent)：
工具调用与回答都使用 greedy 解码、opening tag 预填、结束标签 stop 和严格结果重建。
旧 `agent-json-v1` 裸 JSON 协议已经删除，不保留兼容死代码。

## 3. rwkv_lightning 映射

HTTP adapter 面向 `rwkv_lightning` 的原生续写请求：

- 完整 prompt 放入 `contents` 的唯一元素。
- `max_tokens`、`temperature`、`top_k`、`top_p` 和重复惩罚逐字段映射。
- 第一版固定 `stream: false`。
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
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 并概括项目"
```

远程 Agent 的工具仍在本机执行，但完整 prompt 会包含模型请求过的文件片段并发送到远程
endpoint。选择远程续写即代表显式启用这条数据路径。

`rwkv_lightning_cuda` 的 raw continuation endpoint 是 `/v1/batch/completions`。它直接接收
`contents`，不会像 `/v1/chat/completions` 那样重新渲染 role 和 think 前缀。服务端
`stop_tokens` 接受整数 token ID；客户端显式只发送 EOS `0`，避免服务默认 token 提前截断
Full think，并继续以 decoded text 匹配协议 stop 序列。

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
