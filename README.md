# RWKV-Agent

> 本地优先的 RWKV 工作区 Agent：Go 负责 Conversation、Session 与 Agent 事务，
> 独立的 `librwkv_agent_runtime.dylib` 通过固定版本的 RWKV Mobile tokenizer/sampler
> 与 MLX FFI 执行推理。运行时不依赖 Python、PyTorch、HTTP 服务或外部进程。
>
> CLI、TUI、桌面 App 与浏览器服务共用同一个公开 `api` 包。
>
> [English version](README.en.md)

## 当前状态

- **可用**：Apple Silicon macOS 15+ 源码构建 —— CLI/TUI、Wails V3 桌面 App、headless server。
- **实验性**：只读 Agent 框架与评测，当前 Harness 版本为 `rwkv-agent-eval-v20`。
- **平台**：Windows 尚无可用入口；Linux 已在 CI 验证 `-tags server` 构建（远程
  provider 场景），本地 MLX 模型与桌面窗口尚未落地。
- **分发**：技术链路已经可用，公开分发前仍需确认上游授权并选择项目许可证。

特性速览：

- CLI：`convert` / `run` / `agent` / `agent-eval` / `concurrent` / `bench`
- 推理：直接 mmap `.pth`、显式 MLX 转换、single-model scheduler、continuous batch（最多 8 路活跃 Session）
- 会话：不可变 revision + 原子 `CURRENT` 指针，transcript 是事实源
- Agent：工作区只读工具、`calculator`/`data_query`/`datetime`、可选 Brave/Tavily Web 与 `spawn_agents` 子代理
- 远程：`rwkv_lightning` 原生续写；OpenAI-compatible Chat Completions（可选 build tag）
- 桌面 App：Wails V3 + React + Material Design 3，持久会话、工具轨迹、Web 重试
- 评测：6 个内置 suite + 可复现 trace 产物

第一次使用请直接看 [macOS 从零上手](docs/getting-started-macos.md)。

## 目录

1. [桌面 App](#1-桌面-app)
2. [快速开始与构建](#2-快速开始与构建)
3. [CLI 命令一览](#3-cli-命令一览)
4. [模型加载与转换](#4-模型加载与转换)
5. [REPL 与 Session](#5-repl-与-session)
6. [Agent 框架](#6-agent-框架)
7. [远程 Provider](#7-远程-provider)
8. [Agent 评测](#8-agent-评测)
9. [并发 Dashboard](#9-并发-dashboard)
10. [测试与 CI](#10-测试与-ci)
11. [项目结构](#11-项目结构)
12. [文档导航](#12-文档导航)
13. [分发与许可证](#13-分发与许可证)

## 1. 桌面 App

仓库包含一个 Wails V3 beta + TypeScript + React + Vite 应用，前端为 Material Design 3。
它使用与 CLI/TUI 相同的公开 `api` 包，支持原生 macOS 窗口和不开窗口的 Wails server
两种形态：

```sh
./scripts/build-app.sh
open -n "./dist/RWKV Agent.app" --args --workspace "$(pwd)"

# Browser-only 模式
./dist/rwkv-app-server --host 127.0.0.1 --port 8080
```

构建 App 额外需要 Node.js 26 与 pnpm 11（CI 使用同一版本基线）。主要功能：

- 配置本地 RWKV 模型（`.pth` 或 MLX 目录）或远端 API（RWKV 续写 / OpenAI 兼容），
  显示模型状态，并通过 `GET /v1/models` 拉取远端模型列表。
- 会话与最近项目持久化：完整 committed transcript（含工具调用与结果）按工作区保存，
  重开后恢复；设置与凭证保存为平台 XDG/Known Folder 位置的明文 JSON，Status 事件
  不含密钥。
- 每条消息保留工具轨迹（Tool Trajectory）：调用步骤、参数、状态、失败原因、子代理
  明细，以及 Web 工具的逐次重试（429/5xx 最多 5 次、指数退避、尊重 `Retry-After`）。
- 自定义 HTTP header（例如 Cloudflare Access）与 macOS 系统代理支持。

存储细节、配置说明和开发命令见 [docs/app.md](docs/app.md)。

## 2. 快速开始与构建

环境要求：

- Apple Silicon Mac，macOS 15+
- Xcode（含 Swift 与 Metal Toolchain）
- CMake 3.25+、Ninja
- Go 1.26+
- Node.js 26、pnpm 11（仅构建桌面 App 需要）
- RWKV-7 `.pth` checkpoint，或已转换的 MLX safetensors 模型目录

首次拉取后初始化固定版本的上游依赖，然后检查环境并构建：

```sh
git submodule update --init --recursive

brew install cmake ninja go   # 命令行依赖

./scripts/build-macos.sh --check
./scripts/build-macos.sh
```

默认产物只包含本地 RWKV 和纯续写 provider，不编译或链接 OpenAI SDK。需要调用上游
Chat Completions 时使用可选构建；纯 Go 构建对应同一组 build tag：

```sh
./scripts/build-macos.sh --with-chat-completions
go build ./cmd/rwkv-cli
go build -tags chatcompletions ./cmd/rwkv-cli
```

构建脚本固定 `arm64` 与 `MACOSX_DEPLOYMENT_TARGET=15.0`，从固定 revision 构建带直接
PTH 入口的 MLX FFI，并验证 dylib、rpath、Metal resource、deployment target 与 CLI
help smoke test。缺少 submodule 时会自动初始化；首次构建拉取 MLX Swift 依赖，后续复用
`build/` 缓存。产物如下：

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

`scripts/build-mlx.sh` 仍保留为兼容入口，会转发到 `build-macos.sh`。安装、运行、更新和
常见错误见 [docs/getting-started-macos.md](docs/getting-started-macos.md)。

## 3. CLI 命令一览

| 命令 | 用途 |
| --- | --- |
| `convert` | 读取 PyTorch ZIP/pickle checkpoint，写出 MLX safetensors（不依赖 Python） |
| `run` | 单轮生成或多轮 REPL，支持 `.pth` 与 MLX 目录 |
| `agent` | 本地优先的只读工作区 Agent（TUI/plain） |
| `agent-eval` | 固定 case 的 Agent 评测，产出 run/trace/summary |
| `concurrent` | 1–8 路并发生成与选中续聊 dashboard |
| `bench` | `concurrent` 的 plain 渲染别名，适合脚本与 CI |

```text
rwkv-cli convert --input <RWKV .pth> --output <MLX model directory>
rwkv-cli run --model <RWKV .pth or MLX directory> [--prompt <text> | --session <bundle>]
rwkv-cli agent --model <path or remote model ID> [--prompt <task>] [--ui auto|tui|plain]
rwkv-cli agent-eval --model <path or remote model ID> [--suite boundary|smoke|assistant|bfcl-product|primitive-orig30|primitive-feedback30]
rwkv-cli concurrent --model <RWKV .pth or MLX directory> [--concurrency 1..8]
rwkv-cli bench --model <RWKV .pth or MLX directory> [--concurrency 1..8]
```

## 4. 模型加载与转换

### 直接运行 `.pth`（推荐）

运行不再要求先转换模型：

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/rwkv7-model.pth \
  --session ./sessions/demo.rwkv-session \
  --autosave
```

运行时 mmap 原始 `.pth`，直接把 tensor 装入 MLX，不写出第二份完整权重。第一次加载会在
`~/Library/Caches/RWKV-Agent/pth-index/v1/` 生成一个通常只有几十到几百 KB 的 `.rwkvi`
元数据索引；后续加载通过索引跳过 pickle 元数据解析。缓存 key 绑定原文件绝对路径，索引
内部再校验文件大小与修改时间，checkpoint 变化后自动拒绝旧索引并原位重建。`.pth` 默认
使用发行包里的 RWKV World tokenizer，只有自定义 vocabulary 时才需要传 `--tokenizer`。

### 显式转换（可选）

`convert` 保留给需要独立 MLX safetensors 产物的部署流程：

```sh
./dist/rwkv-cli convert \
  --input /absolute/path/to/rwkv7-model.pth \
  --output /absolute/path/to/rwkv7-model-mlx
```

默认输出 BF16，也可使用 `--precision fp16` 或 `--precision fp32`。目标目录已存在时默认
拒绝覆盖，确认替换可传 `--overwrite`。转换结果包含 `config.json`、
`model.safetensors` 与 `rwkv_vocab_v20230424.txt`。

## 5. REPL 与 Session

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/rwkv7-model.pth \
  --session ./sessions/demo.rwkv-session \
  --autosave
```

主要参数：

```text
--backend auto|rwkvmobile        --provider auto|mlx
--tokenizer <file>               --session <bundle>
--prompt <single turn>           --max-tokens <n>
--temperature <f>                --top-k <n> --top-p <f>
--presence-penalty <f>           --frequency-penalty <f> --penalty-decay <f>
--thinking off|fast|full         --native-state auto|off|required
--autosave
```

默认使用 RWKV 官方 G1 常规聊天模板 `User: ...\n\nAssistant:`。`--thinking fast`
严格预填充 `Assistant: <think></think` 后快速续写，`--thinking full` 严格预填充
`Assistant: <think`；两者最后的 `>` 都**故意不写入 prompt**，由模型生成（RWKV tokenizer
会把 `>` 与后续文本合并切分，补上括号会让续写从一个训练中不存在的 token 边界开始）。
旧参数 `--reasoning[=true|false]` 仍分别兼容 `fast/off`；不要把 `<|bos|>` 等伪 special
token 写进 prompt。

默认解码参数采用当前 G1 模型卡建议：`temperature=1`、`top-p=0.5`、`presence-penalty=2`、
`frequency-penalty=0.1`、`penalty-decay=0.99`。模型加载时显示轻量 spinner；单轮生成和
REPL 不进入 alternate screen，回答是可选择、复制和重定向的普通文本。

REPL 命令：

```text
/state   /history   /save [path]   /load <path>   /reset   /new   /help   /exit
```

每轮先在候选 transcript 上生成，只有完整输出与 native prefix 对齐后才提交。取消、终端
写入失败或 native 错误不会写入残缺 user/assistant 消息。生成时第一次 `Ctrl-C` 只取消
当前 turn 并回到提示符；空闲时 `Ctrl-C` 退出。`SIGTERM` 会先请求取消再按 Session、Model、
Runtime 的顺序关闭。

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
State 加速快照。快照不存在或导入失败时自动 replay transcript；模型、tokenizer、Initial
State 或不支持迁移的 prompt profile 不兼容时拒绝加载。`/load` 使用临时 Conversation
完成校验和恢复，成功后才替换当前会话。同一 `rwkv-g1-chat` 模板的旧 prompt profile 会
安全升级：未显式传 `--thinking` 时继承 Session 原有思考模式；显式模式冲突、模型或
tokenizer 不匹配仍会拒绝。迁移后的 autosave 写入新 revision，不改写旧 revision。

## 6. Agent 框架

`agent` 验证本地优先 Agent 的纵向链路：模型在指定工作区内列出文件、读取文本、搜索
字面量并处理结构化数据，然后基于实际工具结果回答。普通 `agent` 默认注册工作区工具，
以及不依赖 Provider 的 `calculator`、`data_query`、`datetime`。固定 mock 的 `weather`、
`nearest_transit`、`transit_hours`、`fx_convert` 只在可重复的 `assistant` 评测 suite 中
注册。默认工具没有写入、命令执行或真实网络能力。

产品默认使用 G1i 训练原生的 Markdown/function transcript：工具目录位于 `System: Tools:`，
工具调用是 `Assistant:` 后续写的 JSON fenced code block，工具结果以
`User: Function output:` 回填。`inspect` 获得足够证据后直接输出普通 Markdown，不注册
`submit`，因此代码块不会被迫塞入 JSON 参数；`respond` 路由也直接回答。旧
`rwkv-g1i-envelope-v1` XML 协议保留为
`--agent-protocol xml` 的 A/B 兼容模式。

渐进式工具暴露默认开启：每轮先由不暴露具体 schema 的短 Router 在 `workspace`、
`compute`、`web`、`delegate` 能力组中选择零至两个；`respond` 直接进入无工具回答，
`inspect:BUNDLE[+BUNDLE]` 只把所选能力组的 schema 交给模型。当前工具不够时模型可以调用
控制工具 `load_tools` 再加载一个能力组；未暴露工具即使被模型点名也会被拒绝。
`--progressive-tools=false` 恢复固定完整目录。

```sh
./dist/rwkv-cli agent \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project
```

交互终端默认进入全屏 Agent TUI；首轮完成后可直接追问，Harness 会把已提交的
user/assistant/tool transcript 带入后续阶段。`/new` 或 `/reset` 清空当前多轮会话，
`/exit` 退出；`Ctrl-C` 运行时取消当前轮次、空闲时退出。传入 `--prompt` 会自动提交首轮
任务；脚本、pipe 和 CI 自动使用 plain renderer：

```sh
./dist/rwkv-cli agent \
  --ui plain \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 和 docs，概括当前已完成内容与下一步"
```

常用参数：

```text
--max-steps <2..20>                  --progressive-tools[=true|false]
--agent-protocol markdown|xml        --route-max-tokens <n>
--decision-max-tokens <n>            --max-tokens <n>
--workspace <directory>              --thinking off|fast|full（仅 XML 兼容协议）
--ui auto|tui|plain                  --prompt <task>
--web                                --subagents
--semantic-no-tool                   --decision-fake-think
--trace-prompt-bytes <n>
--brave-endpoint <url>               --tavily-endpoint <url>
--max-active-batch <1..8>            --subagent-max-parallel <2..8>
--subagent-max-steps <n>             --subagent-timeout <duration>
--remote-batch-wait <duration>
```

Agent 默认使用确定性解码：`temperature=1`、`top-k=1`、`top-p=1`，presence/frequency
惩罚为 0、`penalty-decay=1`。能力 Router 最多生成 48 token，首次工具选择最多 96 token，
最终回答最多 1024 token，并限制为 6 个 Agent step（Router 独立计数）。产品实验开关默认
关闭；`--few-shot`、旧 `--route-stage` 和 Primitive 的重复/救援参数只属于 `agent-eval`，
不再作为看似可用但实际不进入 App profile 的 `agent` 参数暴露。

Product Markdown profile 固定使用 `--thinking off`；`--thinking fast/full` 只保留给
`--agent-protocol xml` 兼容 A/B。Product 的半开 think 字节实验必须使用独立的
`--decision-fake-think` 开关，避免把两种 renderer 语义混成一套。

### 可选 Web 与子代理

只有显式传入 `--web` 且同时提供两个 API Key 时才注册 `web_search`（Brave Search）与
`web_fetch`（Tavily Extract，最多 4 个页面）：

```sh
export BRAVE_API_KEY='...'
export TAVILY_API_KEY='...'

./dist/rwkv-cli agent \
  --web \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project
```

Web Provider 对 429/5xx 自动重试（最多 5 次、500ms 起指数退避、上限 5s、尊重
`Retry-After`），并把每次重试记录进工具轨迹事件。

`spawn_agents` 一次接收 2–8 个独立任务并发执行，每个任务创建自己的 Session、State 和
transcript，结果按输入顺序返回。子 Agent 继承工作区、计算和 Web 能力，但不继承
`delegate`，因此不会递归派生。全部子任务失败时整个工具调用失败；部分成功时保留成功
输出和逐项错误。本地 MLX 通过 continuous batching 并行推进独立 Session；RWKV Lightning
在聚合窗口内把兼容的并发续写合并成一个 `contents[]` 请求；Chat Completions 则发并发
HTTP 请求。`continuation.Generator` 仍保持单请求、传输中立，批处理只发生在
Provider/runtime 层。

```sh
./dist/rwkv-cli agent \
  --subagents \
  --max-active-batch 4 \
  --subagent-max-parallel 4 \
  --subagent-max-steps 4 \
  --subagent-timeout 2m \
  --remote-batch-wait 10ms \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project
```

### 安全边界与恢复

所有工具路径必须相对 `--workspace`；绝对路径、`..` 穿越和指向工作区外的符号链接都会被
拒绝。单文件读取限制为 64 KiB，搜索跳过 `.git`、`build`、`dist` 和 `node_modules`。
每次工具尝试后 Runner 保留完整的 assistant/function-output 轨迹，允许模型继续调用不同
工具，证据充分时直接回答；失败结果给出确定性恢复提示，同一精确调用不会再次执行。
达到重复或同工具连击阈值后，Runner 禁用后续工具并要求基于已有证据直接给出最佳答案；
证据不足时必须明确说明限制。合法 final 产生后才事务化提交整轮 transcript，生成、协议或 step
失败仍整轮回滚。诊断协议错误可临时设置 `RWKV_AGENT_DEBUG=1`（会打印可能包含本地文件
内容的原始模型 step，默认不启用）。

当前 CLI `agent` 支持进程内多轮交互，但还没有自己的 transcript 保存/恢复；桌面 App 已
通过公开 `api` 持久化会话与历史。上下文压缩、写文件审批和命令执行仍不在范围内。
协议边界、工具权限与状态机设计见
[docs/continuation-and-agent-protocol.md](docs/continuation-and-agent-protocol.md) 与
[docs/agent-harness-milestone.md](docs/agent-harness-milestone.md)。

## 7. 远程 Provider

### rwkv_lightning 原生续写

```sh
# 仅当服务启用请求体密码时：export RWKV_API_PASSWORD='...'
export RWKV_CF_ACCESS_CLIENT_ID='...'      # Cloudflare Access 部署时需要
export RWKV_CF_ACCESS_CLIENT_SECRET='...'

./dist/rwkv-cli agent \
  --completion rwkv-lightning \
  --api-url https://example.com/v1/batch/completions \
  --model rwkv7-13b \
  --api-header-env CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID \
  --api-header-env CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET \
  --workspace /absolute/path/to/project
```

要点：

- `--api-url` 是完整 endpoint，不会自动拼接 OpenAI 路径；客户端按 `contents` 发送，
  `/v1/batch/completions`、`/v1/chat/completions` 与 `/big_batch/completions` 都可能提供
  该语义（用 `GET /openapi.json` 确认）。
- `stop_tokens` 是 **decoded-text 字符串数组**（不是整数 token ID）。默认
  `--api-stop-tokens text` 直接转发本轮协议的 stop 序列；`cuda` 预设用于要求整数 token ID
  的 `rwkv_lightning_cuda` 部署；`none` 省略该字段，`eos` 或逗号分隔整数沿用旧形式。
- `--api-stream` 默认 `true`（SSE 逐 token）；`--api-stream=false` 请求一次性 JSON 响应，
  在 SSE 不稳定的部署上更可靠，但交互式 `agent` 会失去 token 级输出。
- `rwkv_lightning` 在 `top-k=1` 时直接取 argmax，temperature 和 top-p 不参与随机采样。
- 密码默认从 `RWKV_API_PASSWORD` 读取（`--api-password-env` 可改）；`--api-header-env`
  可重复使用，凭证不进入命令行参数或配置文件。远程模型会收到 Agent 组成的 prompt，
  其中可能包含模型主动读取的本地文件片段。

### OpenAI-compatible Chat Completions

```sh
export OPENAI_API_KEY='...'

./dist/rwkv-cli agent \
  --completion chat-completions \
  --api-url https://example.com/v1/chat/completions \
  --model other-model \
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 并概括项目"
```

`chat-completions` 由官方 `github.com/openai/openai-go/v3` SDK 实现，通过
`chatcompletions` build tag 与默认发行包隔离。默认 `--chat-prompt-mode native-chat`
传递真正的 system/user/assistant 消息与原生 `tools`；`wrapped-continuation` 把完整
continuation prompt 放进一个 user message，作为不支持原生工具的兼容回退。两者都使用
非流式响应，固定发送 `parallel_tool_calls: false`；输出预算默认使用
`max_completion_tokens`，只接受旧字段的服务用 `--chat-token-limit-field max-tokens`。

对于默认开启隐藏推理、且隐藏推理与正文共享输出预算的上游（例如 DeepSeek V4-Flash），
应显式关闭上游思考：

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

`--chat-thinking auto`（默认）不发送非标准字段；`disabled`/`enabled` 发送
`thinking: {"type":"..."}` 扩展。它独立于控制内部 RWKV prompt 的
`--thinking off|fast|full`。Bearer token 默认读取 `OPENAI_API_KEY`
（`--api-key-env` 可改）；显式 `Authorization` header 会覆盖 bearer token。

可选的真实接口集成测试默认跳过：

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

完整映射细节见 [docs/continuation-and-agent-protocol.md](docs/continuation-and-agent-protocol.md)。

## 8. Agent 评测

`agent-eval` 按 suite 使用显式 profile。`bfcl-product` 通过和 App 相同的
`ProductHarnessOptions` 入口构造 Markdown/function + progressive Router；Primitive、BFCL
原始包装协议和 XML 回归各自保持独立，避免把 benchmark 字节协议混进产品：

| Suite | 内容 |
| --- | --- |
| `boundary`（默认） | 18 个从 [marty1885/primitive-bench](https://github.com/marty1885/primitive-bench) 只读任务改造的 case |
| `smoke` | 10 个协议与安全契约回归 |
| `assistant` | 6 个天气/交通、开销/汇率、Provider 不可用、单意图与歧义追问 |
| `bfcl-product` | 60 个从 BFCL 语义转化的产品题：主动不调用、缺参追问与多轮决策 |
| `primitive-orig30` | 上游 `agent_cases_orig30` 的 30-case 固定快照（旧名 `primitive` 仍可用） |
| `primitive-feedback30` | 同一上游 commit 的 `agent_cases_feedback` 精选 30 题 |

```sh
./dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite boundary \
  --output runs/local-13b-boundary
```

每个 case 使用独立临时工作区；本地推理为每个 case 创建全新 Session。`--case` 可重复选
子集，`--cases` 可载入 `schema_version: 4` 的自定义 JSON case 文件或受信任的 Primitive
Bench 目录，`--case-timeout` 设单 case 超时，`--case-parallelism` 设并发度。`--cases` 与
`--suite` 互斥；输出目录必须尚不存在。

Case schema v4 可用 `require_active_no_call` 和 `forbid_route_fallback` 把“主动不调用”设为
显式成功条件。Run schema v6 在 manifest 冻结 scorer/outcome taxonomy、产品协议/renderer、
Router 和两个实验开关，并在 summary 分别报告 `active_no_call`、route/decision 协议合法率、
outcome 分布和分类解析失败；`semantic_no_call`、普通文本 final、fail-closed 与兼容修复互不
混记。

`bfcl-product` 默认开启 progressive Router。两个 7B 定向实验开关默认关闭：
`--semantic-no-tool` 允许文本协议输出 `no_tool`，参数只能为空，或包含可选字符串
`reason` / `answer`。非空 `answer` 优先、否则 `reason` 直接成为用户可见最终回复；原始字段
同时保留在 trace 和 App 的“无需工具”事件里，但不算工具执行或 evidence。空参数保留为进入
直接回答阶段的兼容路径，未知字段和非字符串值仍拒绝。`--decision-fake-think` 只在未锚定的
inspect decision 上预填精确的半开 `<think></think`。两者只适用于文本续写，不会注册成
原生 API tool；原生 function calling 会拒绝该组合。显式
`--progressive-tools=false` 可用于无 Router 校准，但此时 route 指标没有分母，不能当作
产品 Router 成绩。

远程评测直接复用同一入口：

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

```sh
export OPENAI_API_KEY='...'

./dist/rwkv-cli agent-eval \
  --completion chat-completions \
  --api-url https://example.com/v1/chat/completions \
  --model other-model \
  --suite primitive-orig30 \
  --output runs/primitive-orig30-external
```

### Primitive Bench 双轨

仓库内置 [`RWKV-Vibe/rwkv-Primitive-Bench`](https://github.com/RWKV-Vibe/rwkv-Primitive-Bench)
commit `416b073d2c5442ae34bfbf8a3b84ed414b5b85ff` 的固定快照，JSON 嵌入 CLI，本地、CI
和外部模型评测使用完全相同的 prompt、fixture 与评分契约，不需要先 clone 上游仓库。

两种显式工具 profile：

- `upstream-compatible`（默认）保留上游逐题声明的完整工具目录（包括 `run_lua`），用于
  协议和 Harness 横向对照。
- `go-native` 保留相同题目、fixture、`max_turns` 和 scorer，但在原题提供 `run_lua` 时以
  `calculator` 与 `data_query` 替代，衡量实际 Go Agent 产品能力，不要求安装 Lua。

```sh
./dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite primitive-orig30 \
  --primitive-profile go-native \
  --output runs/primitive-orig30-local
```

`rwkv_lightning_cuda` 部署要求整数形式的 `stop_tokens`，用 `--api-stop-tokens cuda`
预设即可走同一个 Harness；额外 HTTP header 只从环境变量读取，不写入评测产物。Primitive
suite 逐题采用快照中的原始 `max_turns`（6–22），并用 1024-token 工具调用预算；`run.json`
的 `manifest.harness.tool_profile` 记录实际 profile，避免两种分数被误混。

每次运行原子写入三个文件：

- `run.json`：case 定义、模型指纹（本地可用时）、Harness/协议版本、prompt 配置、采样参数与运行环境。
- `trace.jsonl`：逐次原始 continuation request/output、usage、阶段、Runner 事件和工具结果；不记录密码或认证 header。
- `summary.json`：逐 case/turn 失败原因与答案、route、协议、精确/必需/禁止工具等评分。

失败 case 仍会写完 artifacts，随后命令以非零状态退出。默认输出到带 UTC 时间戳的
`runs/agent-eval-*`。

### 当前基线

- Primitive `upstream-compatible`：v12 有效基线 13/30（7.2B，替换一次网络失败后）；
  native-G1i 协议分支最终 17/30，同一模型上游官方留档 20/30。
- Primitive `go-native`（贪心 `top-k=1`）：正式成绩 23/30（v19/v20 稳定通过集合），
  v21b 单轮 24/30，其中 `config_precedence_resolve` 为不稳定边界题（通过率约 25–30%）。
- `boundary` 与 smoke 的历史演进、v8/v9 修复复测和失败分类，见
  [docs/evaluations/](docs/evaluations/)。

完整的 v12 基线、v13–v21 演进、复跑命令与政策记录见
[docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md](docs/evaluations/primitive-bench-v12-baseline-2026-08-13.md)。

## 9. 并发 Dashboard

`concurrent` 用一个模型实例创建多个 Session，并让 native scheduler 合并单 token decode：

```sh
./dist/rwkv-cli concurrent \
  --model /absolute/path/to/rwkv7-model.pth \
  --concurrency 8 \
  --max-tokens 64 \
  --concurrent-prompt "用一句话介绍 RWKV"
```

终端可交互时默认进入实时 dashboard（2×4 或 4×2 pane，窄终端自动降级），header/footer
显示 provider、native batch 与 aggregate tok/s。初始 8 路完成后，点击满意的 pane 即可
继续追问；该操作复用该 pane 原本的 `Conversation` 和 native State，而不是用输出文本临时
拼新会话。渲染模式：

```text
--ui auto    终端可交互时使用 TUI，否则自动 plain（默认）
--ui tui     强制 TUI；终端能力不足时明确报错
--ui plain   强制稳定纯文本输出，适合 pipe、CI 和脚本
```

`bench` 是 `concurrent` 的 `--ui plain` 别名。Dashboard 快捷键：`q`/`Esc` 退出、
`Tab`/方向键切换 pane、`y` 复制、`r` 重跑、点击或 `Enter` 选中续聊。退出 alternate
screen 后固定打印一行 `Concurrent batch complete: ...` 汇总。

所有窗口收到相同的用户 prompt 和解码参数，只使用 `42 + session_index` 的不同 seed；
session 编号只属于 UI，不会写进模型输入。`--top-k 1` 的贪心解码应得到 8 个相同结果，
去掉 `--top-k 1` 后则出现合理的采样差异。每个 Session 的 callback、采样器、token、取消
标志和 State 彼此隔离；MLX FFI 支持 16 个物理 State slot，CLI 当前开放最多 8 路活跃
batch，并为额外请求提供有界 FIFO 队列。录屏演示建议终端至少 `120×40` cell（`160×24`
以上切换四列），生成中截取 dashboard，完成后再演示点击续聊。

## 10. 测试与 CI

不依赖真实模型：

```sh
go test ./...
go test -race ./...
./scripts/test-macos-native.sh
```

Go 测试包含 8 路 runner、选定 Conversation 续聊与取消回滚、plain 无 ANSI、CJK/emoji
cell 宽度、响应式布局，以及真实 PTY 下的 alternate-screen、resize、鼠标点选续聊、`q`
全局取消和终端恢复。`test-macos-native.sh` 还会构建 AddressSanitizer 版本并运行 C ABI
lifecycle test。

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

真实模型脚本覆盖单轮生成、8 路贪心解码 State 隔离、4 路取消、保存、native State 恢复，
以及移除 `state.bin` 后的 transcript replay。

GitHub Actions（`.github/workflows/ci.yml`）包含两个 job：

- Go：race 测试 `api/...`、`internal/...`、`cmd/rwkv-cli/...`；`CGO_ENABLED=0 go build -tags server ./...` 与 vet 验证 Linux headless 构建。
- Frontend：Node 26 + pnpm 11（`pnpm install --frozen-lockfile` + `pnpm test` + `pnpm build`）。

## 11. 项目结构

```text
api/                  CLI/TUI/桌面 App/浏览器服务共用的公开 Agent API
cmd/rwkv-cli/         CLI 与 TUI 入口
cmd/rwkv-app/         Wails V3 桌面 App（Go 后端 + React/MD3 前端）
internal/
  agent/              Agent Harness、渐进式工具、工具实现
  agent/eval/         评测 suite 与内嵌 Primitive Bench 快照
  appstorage/         桌面 App 的 XDG/Known Folder 持久化
  cli/                命令实现与 TUI
  continuation/       Generator 抽象与 local/rwkvlightning/chatcompletions adapter
  conversation/       transcript、revision 与 session bundle
  inference/          推理核心、backend 抽象与调度
  native/             MLX FFI、converter、rwkvmobile 后端
docs/                 上手、设计、协议、评测与归档文档
native/               C ABI runtime 与 FFI 工程（librwkv_agent_runtime）
scripts/              构建与测试脚本
third_party/rwkv-mobile  固定 revision 的 tokenizer/sampler 上游（submodule）
archive/              历史评测基线归档
```

## 12. 文档导航

| 分类 | 文档 |
| --- | --- |
| 总索引 | [项目文档、评测与跑分索引](INDEX.md) |
| 上手 | [macOS 从零上手](docs/getting-started-macos.md) · [桌面 App](docs/app.md) |
| 设计 | [推理核心设计](docs/inference-core-design.md) · [直接 PTH 加载](docs/direct-pth-loading.md) |
| Agent | [续写接口与 Agent 协议](docs/continuation-and-agent-protocol.md) · [Harness 里程碑](docs/agent-harness-milestone.md) |
| 评测 | [docs/evaluations/](docs/evaluations/)（v12 基线与 v13–v21 演进、API 13B 报告、P0 落地报告） |
| 报告 | [docs/reports/](docs/reports/)（Harness 层优化报告中英版） |
| 归档 | [docs/archive/](docs/archive/)（旧实施计划与验证文档） |

仓库级总索引见 [INDEX.md](INDEX.md)；`docs/` 逐文件索引见
[docs/README.md](docs/README.md)。

## 13. 分发与许可证

当前固定的 `rwkv-mobile` revision 没有在仓库根目录提供明确的 LICENSE 文件。技术打包链
已经可用，但公开分发前仍需确认上游源码、MLX Swift FFI 源码及其依赖的授权条件，并为
RWKV-Agent 选择项目许可证。
