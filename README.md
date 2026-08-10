# RWKV-Agent

RWKV-Agent 当前提供一个可分发的 Apple Silicon macOS 本地 CLI。Go 负责 Conversation 事务、Session 持久化和终端交互；独立的 `librwkv_agent_runtime.dylib` 通过固定版本的 RWKV Mobile tokenizer/sampler 与 MLX FFI 执行推理。运行时不依赖 Python、PyTorch、HTTP 服务或外部进程。

> 当前真正可用的是 Apple Silicon macOS 15+ 源码构建；Windows 和 Linux 是目标平台，
> 但还没有可用入口。第一次使用请直接看
> [`macOS 从零上手`](docs/getting-started-macos.md)。

```text
rwkv-cli
  → Conversation（transcript / revision / rollback / replay）
  → inference backend
  → versioned C ABI + per-request callback
  → single-model scheduler
  → MLX continuous batch（最多 8 个活跃 Session）
```

详细设计和验收范围见：

- [`docs/getting-started-macos.md`](docs/getting-started-macos.md)
- [`docs/inference-core-design.md`](docs/inference-core-design.md)
- [`docs/direct-pth-loading.md`](docs/direct-pth-loading.md)
- [`docs/rwkv-mobile-adoption-and-cli-milestone.md`](docs/rwkv-mobile-adoption-and-cli-milestone.md)
- [`docs/rwkv-mobile-macos-cli-implementation-plan.md`](docs/rwkv-mobile-macos-cli-implementation-plan.md)
- [`docs/rwkv-cli-tui-redesign-plan.md`](docs/rwkv-cli-tui-redesign-plan.md)
- [`docs/agent-harness-milestone.md`](docs/agent-harness-milestone.md)
- [`docs/continuation-and-agent-protocol.md`](docs/continuation-and-agent-protocol.md)

## 环境

- Apple Silicon Mac
- macOS 15+
- Xcode（包含 Swift 与 Metal Toolchain）
- CMake 3.25+
- Ninja
- Go 1.26+
- RWKV-7 `.pth` checkpoint，或已转换的 MLX safetensors 模型目录

首次拉取后初始化固定版本的上游依赖：

```sh
git submodule update --init --recursive
```

命令行依赖可通过 Homebrew 安装：

```sh
brew install cmake ninja go
```

## 构建

先检查环境，不进行编译：

```sh
./scripts/build-macos.sh --check
```

然后构建：

```sh
./scripts/build-macos.sh
```

默认产物只包含本地 RWKV 和纯续写 provider，不编译或链接 OpenAI SDK。需要调用上游
Chat Completions 时使用可选构建：

```sh
./scripts/build-macos.sh --with-chat-completions
```

纯 Go 构建对应为 `go build ./cmd/rwkv-cli` 与
`go build -tags chatcompletions ./cmd/rwkv-cli`。依赖仍由同一个 `go.mod` 锁定版本，但无 tag
的二进制不含 SDK 代码；若在默认构建中选择 `--completion chat-completions`，CLI 会明确提示
用 `-tags chatcompletions` 重建。

构建脚本固定 `arm64` 和 `MACOSX_DEPLOYMENT_TARGET=15.0`，从固定 revision 构建带直接
PTH 入口的 MLX FFI，并验证 dylib、rpath、Metal resource、deployment target 和 CLI
help smoke test。缺少 submodule 时会自动初始化。首次构建会拉取 MLX Swift 依赖，后续
复用 `build/` 中的构建缓存；旧版留下的部分补丁缓存也会自动修复。产物如下：

```text
dist/
├── rwkv-cli
├── librwkv_agent_runtime.dylib
├── build-manifest.json
├── assets/
│   └── rwkv_vocab_v20230424.txt
└── mlx-swift_Cmlx.bundle/
    └── Contents/Resources/default.metallib
```

`scripts/build-mlx.sh` 仍保留为兼容入口，但会转发到 `build-macos.sh`。
安装、运行、更新和常见错误的完整说明见
[`docs/getting-started-macos.md`](docs/getting-started-macos.md)。

## 直接运行 `.pth`（推荐）

运行不再要求先转换模型：

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/rwkv7-model.pth \
  --session ./sessions/demo.rwkv-session \
  --autosave
```

运行时 mmap 原始 `.pth`，直接把 tensor 装入 MLX，不写出第二份完整权重。第一次加载会在
`~/Library/Caches/RWKV-Agent/pth-index/v1/` 生成一个 `.rwkvi` 元数据索引；索引记录
tensor 名称映射、shape、dtype、storage key 和 offset，通常只有几十到几百 KB。后续加载
通过索引跳过 pickle 元数据解析。缓存 key 绑定原文件的绝对路径，索引内部再校验文件大小
与修改时间；checkpoint 变化后会自动拒绝旧索引并原位重建，不会不断累积完整权重副本。

`.pth` 默认使用发行包里的 RWKV World tokenizer；只有自定义 vocabulary 时才需要传
`--tokenizer`。

## 显式转换（可选）

`convert` 保留给需要独立 MLX safetensors 产物的部署流程。转换器直接读取 PyTorch
ZIP/pickle checkpoint 并写出 MLX safetensors，不加载 Python 或 PyTorch：

```sh
./dist/rwkv-cli convert \
  --input /absolute/path/to/rwkv7-model.pth \
  --output /absolute/path/to/rwkv7-model-mlx
```

默认输出 BF16，也可使用 `--precision fp16` 或 `--precision fp32`。目标目录已存在时默认拒绝覆盖；确认替换可传 `--overwrite`。转换结果包含：

```text
rwkv7-model-mlx/
├── config.json
├── model.safetensors
└── rwkv_vocab_v20230424.txt
```

## 运行多轮 REPL

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/rwkv7-model.pth \
  --session ./sessions/demo.rwkv-session \
  --autosave
```

主要参数：

```text
--backend auto|rwkvmobile
--provider auto|mlx
--tokenizer <file>
--session <bundle>
--prompt <single turn>
--max-tokens <n>
--temperature <f>
--top-k <n>
--top-p <f>
--presence-penalty <f>
--frequency-penalty <f>
--penalty-decay <f>
--thinking off|fast|full
--autosave
--native-state auto|off|required
```

默认使用 RWKV 官方 G1 常规聊天模板 `User: ...\n\nAssistant:`。`--thinking fast`
预填充完整的 `Assistant: <think></think>` 后快速续写；`--thinking full`
预填充 `Assistant: <think>`，由模型生成思考内容、闭合 `</think>` 并回答。RWKV 已原生训练
该思考格式，因此框架给出完整标签，不再留半个标签让模型补齐。旧参数
`--reasoning[=true|false]` 仍分别兼容 `fast/off`；不要把 `<|bos|>` 等伪 special token
写进 prompt。

默认解码参数采用当前 G1 模型卡的聊天建议：
`temperature=1`、`top-p=0.5`、`presence-penalty=2`、
`frequency-penalty=0.1`、`penalty-decay=0.99`。

模型加载时，交互终端显示轻量 spinner；单轮生成和 REPL 不进入 alternate screen，模型回答
仍是可直接选择、复制和重定向的普通文本。非交互环境不输出颜色或光标控制序列。

REPL 命令：

```text
/state
/history
/save [path]
/load <path>
/reset
/new
/help
/exit
```

每轮先在候选 transcript 上生成，只有完整输出与 native prefix 对齐后才提交。取消、终端写入失败或 native 错误不会写入残缺 user/assistant 消息；dirty State 会在下一轮或保存前从已提交 transcript 重建。

生成时第一次 `Ctrl-C` 只取消当前 turn 并回到提示符。空闲时 `Ctrl-C` 退出。`SIGTERM` 会先请求取消再按 Session、Model、Runtime 的顺序关闭。

## Session bundle

Session 使用不可变 revision 和原子 `CURRENT` 指针：

```text
demo.rwkv-session/
├── CURRENT
└── revisions/
    └── sha256-.../
        ├── session.json
        ├── transcript.jsonl
        └── state.bin
```

transcript 是事实源，`state.bin` 只是带 codec、尺寸、prefix token 和 checksum 校验的 MLX
State 加速快照。快照不存在或导入失败时会自动 replay transcript；模型、tokenizer、
Initial State 或不支持迁移的 prompt profile 不兼容时拒绝加载。`/load` 使用临时
Conversation 完成校验和恢复，成功后才替换当前会话。

同一 `rwkv-g1-chat` 模板的旧 prompt profile 会安全升级：CLI 校验旧 transcript 和 logical
revision，丢弃旧版 native State，再用当前 profile replay。未显式传 `--thinking` 时会
继承 Session 原有的思考模式；显式模式冲突、模型或 tokenizer 不匹配仍会拒绝。
迁移后的 autosave 写入新 revision，不会原地改写旧 revision。

## 实验性本地优先 Agent 框架

`agent` 命令用于验证第一条 Agent Harness 纵向链路：模型可以在指定工作区内列出文件、
读取文本、搜索字面量和确定性处理结构化数据，然后基于实际工具结果回答。P0 还注册了
`weather`、`nearest_transit`、`transit_hours`、`fx_convert`、`calculator`、
`structured_query` 和 `datetime`。天气、交通和汇率目前使用固定 mock Provider，只用于
可重复评测，不代表实时数据；工具没有写入、命令执行或真实网络能力。
Agent 只依赖“文本前缀 -> 续写文本”的窄接口，本地模型和 `rwkv_lightning` HTTP 是两种
可替换 adapter。当前 `rwkv-g1i-envelope-v1` 采用 G1I 已验证的文本 envelope：
`<tool_call>{"name":...,"arguments":...}</tool_call>` 和
`Tool: <tool_result>...</tool_result>`。第一轮普通文本直接作为最终回答，不要求套
envelope；因此用户询问 Agent 能力时不需要虚构一次工具调用。

每轮先由一个不暴露工具 schema 的短 Router prompt 让模型选择 `respond` 或 `inspect`。
`respond` 使用完全无工具的普通回答 prompt；`inspect` 才进入工具选择阶段。Router 只读取
最近的已提交 user/assistant 历史，不接收原始工具正文；格式连续失败时安全降级为
`respond`，Harness 不根据关键词猜测用户意图。成功执行只读工具后，Runner 使用独立
的短回答 prompt，并按任务相关性压缩过长字符串，再预填 `<answer>`；工具路由示例和完整
大文件不会继续占用回答阶段上下文。Router 明确选择 `inspect` 后，Runner 会在第一次工具
选择续写前预填 `<tool_call>`，模型只需继续生成 JSON 和 closing tag，Runner 再重建并
严格解析完整控制帧。旧裸 JSON 动作协议已在真实 13B 验证通过后移除。

```sh
./dist/rwkv-cli agent \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project
```

交互终端默认进入全屏 Agent TUI。首轮完成后可直接追问；Harness 会把已提交的
user/assistant/tool transcript 带入后续工具选择和最终回答阶段。取消或失败的轮次不会写入
会话历史。输入 `/new` 或 `/reset` 可清空当前多轮会话，`/exit` 可退出；`Ctrl-C` 在运行时
取消当前轮次，空闲时退出。

传入 `--prompt` 时会自动提交首轮任务。脚本、pipe 和 CI 自动使用 plain renderer，并要求
显式提供 prompt；也可以手动选择：

```text
--ui auto|tui|plain
```

```sh
./dist/rwkv-cli agent \
  --ui plain \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 和 docs，概括当前已完成内容与下一步"
```

Agent 默认使用 `temperature=1`、`top-k=1`、`top-p=1` 的确定性解码，presence/frequency
惩罚为 0，`penalty-decay=1`。Router 最多生成 16 token，首次工具选择最多生成 96 token，
最终回答最多生成 1024 token，并限制为 6 个 Agent step（Router 独立计数）。
`rwkv_lightning` 在 `top-k=1` 时直接取 argmax，因此 temperature 和 top-p 不参与随机
采样。可用参数包括：

```text
--max-steps <2..20>
--route-stage[=true|false]
--route-max-tokens <n>
--decision-max-tokens <n>
--max-tokens <n>
--workspace <directory>
--thinking off|fast|full
```

`--route-stage` 在 decision 之前额外跑一次 respond/inspect 分类调用，默认关闭。它是早期
为小模型加的引导脚手架，每轮多花一次模型调用；13B 级模型在 decision 阶段内部就能正确
判断该不该调工具。rwkv7-g1i-13.3b 实测：boundary 两种模式都是 13/18，但关闭后模型调用
由 69 降到 48、耗时由 345s 降到 250s、协议合规由 96.1% 升到 100%，失败集合完全相同；
assistant 由 2/6 升到 3/6，唯一差异是 `as_ambiguous_needs_clarify` —— 模型行为本身正确
（追问城市、零工具调用），但 route 阶段把它判成 `inspect`，case 仅因 route 断言失败。
更小的模型可以用 `--route-stage` 重新开启。开启时 route 判分和断言才生效：关闭时每轮带的
是硬编码 `inspect` 默认值，计入 route 准确率会白送一个 100%，因此 summary 记为 `n/a`，
manifest 里同时记录 `route_stage`。

使用 `rwkv_lightning` 的原生续写接口：

```sh
# 仅当服务启用请求体密码时：export RWKV_API_PASSWORD='...'
# 仅当 endpoint 使用 Cloudflare Access 时：
export RWKV_CF_ACCESS_CLIENT_ID='...'
export RWKV_CF_ACCESS_CLIENT_SECRET='...'

./dist/rwkv-cli agent \
  --completion rwkv-lightning \
  --api-url https://example.com/v1/batch/completions \
  --model rwkv7-13b \
  --api-header-env CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID \
  --api-header-env CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET \
  --workspace /absolute/path/to/project
```

`--api-url` 是完整 endpoint，不会自动拼接 OpenAI 路径。`rwkv_lightning_cuda` 必须使用接收
`contents` 数组的 raw continuation 路径，客户端正是按 `contents` 发送的。路径取决于部署，
可用 `GET /openapi.json` 确认：`/v1/batch/completions`、`/v1/chat/completions` 与
`/big_batch/completions` 都可能提供该语义。注意只要请求体传 `contents`（而不是
`messages`），`/v1/chat/completions` 同样是逐 token 续写，不会重新套 chat 模板或 think
前缀；传 `messages` 才会。`/big_batch/completions` 语义相同但单请求串行，评测建议用
`/v1` 路径。

`rwkv_lightning` 的 `stop_tokens` 是 **decoded-text 字符串数组**（上游示例为
`["\nUser:"]`），不是整数 token ID；发整数会让服务返回 HTTP 500。默认
`--api-stop-tokens text` 直接转发本轮协议的 stop 序列，让服务端提前停止生成，而不是一路
生成到 `max_tokens` 再由客户端截断。其他取值：`none` 省略该字段，`eos` 或逗号分隔的整数
列表沿用旧的 token ID 形式（仅用于兼容接受整数的部署）。客户端始终保留 decoded-text 收束
作为兜底。`/big_batch/completions` 只支持 `temperature`，且单请求串行、并发返回 HTTP 409，
所以评测应使用支持全部采样参数的 `/v1/chat/completions`。

`--api-stream` 默认 `true`，走 SSE 逐 token 流式。`--api-stream=false` 改为请求一次性
JSON 响应：客户端在完整文本上做一次 decoded-text stop 截断，并优先采信响应里的
`finish_reason`。评测只需要最终文本，因此在流式通路不稳定的部署上应使用非流式——实测
该部署的 SSE 在一定负载后会退化为 HTTP 200 空响应体，而非流式路径不受影响。交互式
`agent` 模式会因此失去 token 级输出。

密码默认从
`RWKV_API_PASSWORD` 读取，也可用 `--api-password-env` 指定其他环境变量；服务没有请求体
密码时可以不设置。`--api-header-env` 可重复使用，将部署层认证请求头绑定到环境变量，
凭证不会进入命令行参数或配置文件。远程模型只会收到 Agent 组成的 prompt，但其中会包含
模型主动读取的本地文件片段。

使用上游 OpenAI-compatible Chat Completions 接口测试其他模型：

```sh
export OPENAI_API_KEY='...'

./dist/rwkv-cli agent \
  --completion chat-completions \
  --api-url https://example.com/v1/chat/completions \
  --model other-model \
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 并概括项目"
```

对于默认启用隐藏推理、且隐藏推理与正文共享输出预算的服务，应显式关闭上游思考，
避免短路由和工具控制帧在产出正文前耗尽 token。例如 DeepSeek V4-Flash：

```sh
export DEEPSEEK_API_KEY='...'

./dist/rwkv-cli agent \
  --completion chat-completions \
  --api-url https://api.deepseek.com/v1/chat/completions \
  --api-key-env DEEPSEEK_API_KEY \
  --model deepseek-v4-flash \
  --chat-thinking disabled \
  --chat-prompt-mode native-chat \
  --chat-token-limit-field max-tokens \
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 并概括项目"
```

`chat-completions` 由官方 `github.com/openai/openai-go/v3` SDK 实现，并通过
`chatcompletions` build tag 与默认发行包隔离。它是外层兼容适配器，不改变本地
continuation 和 G1I 基线，并支持两种
prompt transport：

- `--chat-prompt-mode native-chat` 是默认值。它传递真正的 system/user/assistant 消息，并按
  Chat Completions 原生协议发送 `tools`。模型调用工具时必须返回 `assistant.tool_calls` 和
  `finish_reason: "tool_calls"`；本地执行后，下一轮使用匹配的 `role: "tool"` 与
  `tool_call_id` 回传 JSON 结果。
- `--chat-prompt-mode wrapped-continuation` 是不支持原生工具的兼容回退。它把 Runner 渲染的
  完整 prompt 放进一个 user message，并继续使用项目自有 G1I 文本控制帧。

原生模式将工具参数声明为 JSON Schema；能满足 Structured Outputs 子集的工具启用
`strict: true`。当前 Harness 每个模型 step 只接受一个动作，因此请求固定发送
`parallel_tool_calls: false`：首次已路由到 `inspect` 时使用 `tool_choice: "required"`，
取得结果后的决策使用 `auto`，最终回答阶段不再发送工具。客户端会在执行前校验调用 ID、
函数名、`finish_reason` 与 JSON 对象参数。若兼容服务忽略 `parallel_tool_calls: false` 仍返回
多个合法调用，adapter 只接纳第一个并让后续调用回到下一轮串行决策；其他不一致响应仍会
被拒绝。
字段与消息顺序以 OpenAI 的 [Function calling guide](https://developers.openai.com/api/docs/guides/function-calling)
和 [Create chat completion reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
为基准。

两种模式都使用非流式响应；`temperature`、`top_p`、presence/frequency penalty、stop 和
seed 会映射到上游，非标准的 `top_k` 与 `penalty_decay` 不会发送。评测产物会将实际模式
记录在 `prompt_mode`，因此可以直接做 wrapped/native A/B。`native-chat` 当前要求内部
`--thinking off`；上游思考仍由独立的 `--chat-thinking` 控制。

输出预算默认使用 OpenAI 当前文档推荐的 `max_completion_tokens`。仅当兼容服务仍只接受
已弃用的 `max_tokens` 时，显式设置 `--chat-token-limit-field max-tokens`；评测 manifest
会记录最终字段，避免不同接口配置被混为同一基线。

`--chat-thinking auto` 是默认值，不发送非标准字段，适用于普通 OpenAI-compatible 服务；
`disabled` 或 `enabled` 会发送 `thinking: {"type":"..."}`，用于支持该扩展的上游。
在 `enabled` 模式下，adapter 会保存并在工具结果轮回传上游的 `reasoning_content`；由于
DeepSeek thinking mode 不接受 `tool_choice: "required"`，该组合会在 wire 层降为 `auto`，
其余模式保持 Runner 请求的选择不变。
这与 `--thinking off|fast|full` 不同：`--chat-thinking` 控制上游服务是否生成隐藏推理，
`--thinking` 控制本项目内部 RWKV prompt 和 G1I 思考协议。若上游不支持 `thinking`
扩展，应保留 `auto`；不要依赖 endpoint 或模型名的隐式厂商检测。

Bearer token 默认读取 `OPENAI_API_KEY`，可通过 `--api-key-env` 指定其他环境变量。无需
Bearer token 的本地服务可以不设置该变量；自定义网关认证仍可使用可重复的
`--api-header-env HEADER=ENV_VAR`，显式的 `Authorization` header 会覆盖 bearer token。

可选的真实接口集成测试默认跳过。配置 endpoint、模型和凭证后可复验同一 adapter；
对 DeepSeek V4 应同时设置 `CHAT_COMPLETIONS_INTEGRATION_THINKING=disabled`：

```sh
export CHAT_COMPLETIONS_INTEGRATION_URL=https://api.deepseek.com/v1/chat/completions
export CHAT_COMPLETIONS_INTEGRATION_MODEL=deepseek-v4-flash
export CHAT_COMPLETIONS_INTEGRATION_API_KEY='...'
export CHAT_COMPLETIONS_INTEGRATION_THINKING=disabled
export CHAT_COMPLETIONS_INTEGRATION_PROMPT_MODE=native-chat
export CHAT_COMPLETIONS_INTEGRATION_TOKEN_LIMIT_FIELD=max-tokens
go test -tags chatcompletions ./internal/continuation/chatcompletions \
  -run 'TestRemoteChatCompletions(NativeTool)?Integration' -v
```

本地 continuation 与 `wrapped-continuation` 中，只有以 `<tool_call>` 开头的输出会进入
严格 envelope/JSON 解析；其余正常文本是最终回答。畸形工具控制帧只重试一次，之后明确
失败。`native-chat` 则先校验官方结构化 tool call，再转换为同一内部 Action。动作协议、RWKV prompt 渲染器和续写
传输分别版本化，未来可以替换工具格式而不修改本地或 HTTP generator。所有工具路径必须
相对 `--workspace`；绝对路径、
`..` 穿越和指向工作区外的符号链接都会被拒绝。单文件读取限制为 64 KiB，搜索跳过
`.git`、`build`、`dist` 和 `node_modules`。

每次工具尝试后，Runner 保留完整的本轮 assistant/tool 轨迹，并允许模型继续调用另一个
不同工具或直接回答。每个成功结果后都会提醒模型只为明确缺失的事实继续调用。失败结果
会给出确定性的恢复提示；`read_file` 路径不确定时优先提示使用 `list_files` 或
`search_text` 发现真实路径。同一精确调用无论此前成功或失败都不会再次执行，并直接触发
收束；同一工具连续执行失败两次后，第三次会被 Controller 拒绝，模型必须改用其他工具或
回答限制。只要本轮发生过工具尝试，最后一个 Agent step 都会保留给禁用工具、预填
`<answer>` 的强制回答阶段，证据不足时必须明确说明。成功生成最终回答后才事务化提交整轮
transcript；生成、协议或 step 失败仍整轮回滚。

诊断模型协议错误时可临时设置 `RWKV_AGENT_DEBUG=1`；它会在失败时打印原始模型 step，
其中可能包含本地文件内容，默认不会启用。

### Agent 评测与 trace

`agent-eval` 使用与 `agent` 完全相同的 Router、prompt、采样和 Runner 参数运行固定
case。默认 `boundary` suite 有 18 个从
[`marty1885/primitive-bench`](https://github.com/marty1885/primitive-bench)
只读任务改造的 case，覆盖发现/搜索、多文件、CSV/JSON/JSONL、财务计算、日志、配置
优先级和 prompt injection。`smoke` suite 保留原来的 10 个协议与安全契约回归；新增的
6-case `assistant` suite 覆盖天气/交通、开销/汇率、Provider 不可用、单意图和歧义追问：

```sh
./dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite boundary \
  --output runs/local-13b-boundary
```

每个 case 使用独立临时工作区；本地推理还会为每个 case 创建全新的 Session，只有同一
case 的多个 turn 共享 transcript/State。可以用可重复的 `--case` 跑子集，用
`--case-timeout` 设置单 case 超时，也可以用 `--cases` 载入
`schema_version: 3` 的自定义 JSON case 文件。`--cases` 与 `--suite` 互斥；输出目录
必须尚不存在，避免覆盖已有基线。

```sh
./dist/rwkv-cli agent-eval \
  --suite smoke \
  --completion rwkv-lightning \
  --api-url https://example.com/v1/batch/completions \
  --model rwkv7-13b \
  --case read_exact_file \
  --case multi_turn_memory \
  --output runs/remote-13b-smoke
```

Chat Completions 模型使用同一套评测：

```sh
./dist/rwkv-cli agent-eval \
  --suite smoke \
  --completion chat-completions \
  --api-url https://example.com/v1/chat/completions \
  --model other-model \
  --output runs/chat-other-model-smoke
```

每次运行原子写入三个文件：

- `run.json`：精确 case 定义、模型指纹（本地可用时）、Harness/协议版本、prompt 配置、
  采样参数和运行环境。
- `trace.jsonl`：逐次原始 continuation request/output、usage、阶段、Runner 事件和工具
  结果；不记录 HTTP 密码或认证 header，但可能包含 case 文件内容。
- `summary.json`：逐 case/turn 失败原因，以及答案、route、协议、精确/必需/禁止工具、
  必需调用参数、no-call、显式弃答、plan 和答案契约修复率。

失败 case 仍会写完 artifacts，随后命令以非零状态退出。默认输出到带 UTC 时间戳的
`runs/agent-eval-*`。

2026-07-30 的 `rwkv-g1i-13b-4922` 结果：

- `smoke`：10/10，只证明 Router、协议、工具和隔离链路可用。
- 固定在第一次成功工具后回答的 `boundary` 基线：4/18；答案 6/18，必需工具 15/22，
  必需调用 15/23，26 次工具调用中 9 次错误。
- 完全开放多工具循环的 `boundary` 对照：10/18；答案 10/18，必需工具 20/22，
  必需调用 21/23，但工具调用增至 65 次、错误增至 32 次，8 个失败 case 都耗尽 step
  且没有最终回答。

这两轮都保持 route 和协议动作 100% 正确，说明前一版主要有框架侧的单工具上限，而完全
放开后又暴露出 13B 在证据足够时继续调用的偏置。当前 `rwkv-agent-eval-v4` 使用上述混合
状态机；同一套 18 题实测仍为 10/18，必需工具和调用保持 20/22、21/23，但工具调用降至
54 次、错误降至 23 次。原先 8 个 step 耗尽且无回答的失败降至 1 个；`pb_csv_sum` 恢复
通过，`pb_markdown_release_notes` 因输出了正确 flag 外的解释而被精确判分判错。该结果
证明收束机制有效，但没有提高本轮总分，仍不能作为发布门槛。

`rwkv-agent-eval-v5` 在 v4 上增加了 `inspect` 首次工具前缀预填、失败恢复
提示、失败/重复调用保护和“任何工具尝试都预留最终回答”的收束规则，并在 summary 中区分
工具请求、实际执行、Controller 拒绝、重复调用、连续失败阻断和强制回答。同一 13B
`boundary` suite 实测仍为 10/18，8 个失败 case 集合没有变化；答案分项由 10/18 升至
11/18，必需工具由 20/22 升至 21/22，必需调用由 21/23 升至 22/23。工具请求由 54 降至
50、错误由 23 降至 15，原先唯一的 step 超限空答案降至 0；38 次实际执行之外有 12 次
重复调用被 Controller 拒绝，14 个 turn 进入强制回答。说明 v5 改善了失败收束和调用效率，
但尚未提高端到端任务通过率。

v5 `smoke` 严格评分为 4/10，但 11/11 回答、route 和协议动作均正确；6 个失败均因模型在
已有足够证据后继续调用额外工具，不是答案或协议错误。这也说明早期 10/10 smoke 结果依赖
“一次成功工具后立即回答”的状态机，不能直接作为当前顺序多工具状态机的回归门槛。

`rwkv-agent-eval-v6` 引入真实性保护：工具参数校验错误会返回该工具的精确参数形状，
并允许修正后的同工具调用继续执行；参数校验失败不再计入运行时连续失败预算，也不视为
工作区证据。若 `inspect` 轮的全部调用都未观察到可信工作区状态，Runner 会以
`ErrNoWorkspaceEvidence` 失败并回滚整轮，而不是让模型猜测答案并污染后续多轮历史。

当前评测版本 `rwkv-agent-eval-v7` 进一步增加默认关闭的 `--few-shot` A/B 开关。
该 profile 在初始决策、成功工具结果后和强制回答阶段注入完整轨迹或输出格式示例。13B
实测中，smoke 严格通过由 4/10 升至 5/10，工具请求由 21 降至 16；但 boundary 由
10/18 降至 7/18，答案由 11/18 降至 8/18。模型会复制示例中的 `notes/title.txt` 和
`EMBER-7`，说明完整静态轨迹产生了明显 prompt anchoring。该开关仅保留用于实验和复现，
默认不启用。

当前 Agent 已支持进程内多轮只读交互，但还没有 transcript 保存/恢复、上下文压缩、
写文件审批或命令执行。后续实施顺序与验收门槛见 Agent Harness 里程碑文档。

## 1–8 路并发与选中续聊

`concurrent` 命令用一个模型实例创建多个 Session，并让 native scheduler 合并单 token decode：

```sh
./dist/rwkv-cli concurrent \
  --model /absolute/path/to/rwkv7-model.pth \
  --concurrency 8 \
  --max-tokens 64 \
  --concurrent-prompt "用一句话介绍 RWKV"
```

当 stdin/stdout 都是可交互终端时，命令默认进入实时 dashboard。8 路在常见宽终端显示
2×4 pane，超宽终端显示 4×2 pane；窄终端自动切换为单列或 compact 列表。每个 pane
独立显示 phase、输出、token、decode 速度、耗时和 finish reason；header/footer 显示
provider、全局 phase、native batch 和 aggregate tok/s。

```text
 model-mlx · MLX · Continuous Batch 8 · completed               00:02.1

╭────────────────────────────╮ ╭────────────────────────────╮
│ Session 1 · done           │ │ Session 2 · done           │
│ RWKV 是一种基于 RNN 的…    │ │                            │
│ 31 tokens · 22.4 tok/s     │ │ 0 tokens                   │
╰────────────────────────────╯ ╰────────────────────────────╯

 ... Session 3–8 ...

 native batch 8/8 · total 221 tokens · aggregate 92.1 tok/s
 click/Enter continue · q quit · r rerun · y copy
```

初始 8 路完成后，直接用鼠标点击满意的 pane，底部会出现输入框；输入问题并按 Enter，
回答会继续流入同一个 pane。这个操作复用该 pane 原本的 `Conversation` 和 native
State，而不是用输出文本临时拼一个新会话。回答完成后输入框会再次打开，可以连续追问；
按 Esc 离开输入框，再按 q 退出。没有鼠标时，用 Tab/方向键选中 pane，再按 Enter。

渲染模式：

```text
--ui auto    终端可交互时使用 TUI，否则自动 plain（默认）
--ui tui     强制 TUI；终端能力不足时明确报错
--ui plain   强制稳定纯文本输出，适合 pipe、CI 和脚本
```

Dashboard 快捷键：

```text
Ctrl-C / q / Esc   运行中取消全部 session，并在回滚完成后退出
Tab / ← / →        切换当前 pane
↑ / ↓ / PgUp/PgDn  滚动当前 pane 的长输出
y                  复制当前 session 的完整输出（macOS）
鼠标点击 / Enter   全部完成后选择当前 pane 并继续对话
Esc                输入时放弃本次提问
q / Esc            未在输入时退出 dashboard
r                  使用相同参数重新运行
```

退出 alternate screen 后固定打印：

```text
Concurrent batch complete: sessions=8 max_native_batch=8 tokens=128 elapsed=2.756s aggregate=46.4 tok/s
```

所有窗口收到完全相同的用户 prompt 和解码参数，只使用 `42 + session_index` 的不同
seed；session 编号只属于 UI，不会写进模型输入。因此常规采样允许措辞不同，而
`--top-k 1` 的贪心解码应得到相同结果。每个 Session 的 callback、采样器、token、取消
标志和 State 彼此隔离。动态加入 batch 的 prefill 会保存并恢复全部活跃物理 State slot，
不会再污染其他窗口。MLX FFI 支持 16 个物理 State slot；CLI 当前开放最多 8 路活跃
batch，并为额外请求提供有界 FIFO 队列。

截图或录屏时，8 路建议先把终端调整到至少 `120×40` cell；`160×24` 以上会切换为四列。
生成过程中截取 dashboard，完成后再演示点击某个结果继续追问。`80×24` 可用于记录
compact 降级和 resize 行为。

排查“相同问候却出现多国语言”时，可先用贪心解码做隔离性验证：

```sh
./dist/rwkv-cli concurrent \
  --model /absolute/path/to/rwkv7-model.pth \
  --concurrency 8 \
  --concurrent-prompt "你好" \
  --top-k 1 \
  --max-tokens 32 \
  --ui plain
```

8 个结果应一致；去掉 `--top-k 1` 后，seed 不同会产生合理的采样差异。

## 测试

不依赖真实模型：

```sh
go test ./...
go test -race ./...
./scripts/test-macos-native.sh
```

Go 测试包含 8 路 runner、选定 Conversation 续聊与取消回滚、plain 无 ANSI、
CJK/emoji cell 宽度、响应式布局，以及真实 PTY 下的 alternate-screen、resize、鼠标
点选续聊、`q` 全局取消和终端恢复。`test-macos-native.sh` 还会构建 AddressSanitizer
版本并运行 C ABI lifecycle test。

使用已转换模型：

```sh
RWKV_TEST_MODEL=/absolute/path/to/mlx-model \
./scripts/test-macos-real-model.sh
```

直接使用 `.pth`：

```sh
RWKV_TEST_PTH=/absolute/path/to/rwkv7-model.pth \
./scripts/test-macos-real-model.sh
```

真实模型脚本让 `.pth` 直接进入运行时，并覆盖单轮生成、8 路贪心解码 State 隔离、
4 路取消、保存、native State 恢复，以及移除 `state.bin` 后的 transcript replay。

## 分发注意

当前固定的 `rwkv-mobile` revision 没有在仓库根目录提供明确的 LICENSE 文件。技术打包链
已经可用，但公开分发前仍需确认上游源码、MLX Swift FFI 源码及其依赖的授权条件，并为
RWKV-Agent 选择项目许可证。
