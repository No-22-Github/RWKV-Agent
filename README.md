# RWKV-Agent

本地优先的 RWKV 工作区 Agent。在 Mac 上直接加载 RWKV-7 `.pth`，用 MLX 推理，让模型在
你指定的项目目录里读文件、搜索、计算、查网页，再基于真实工具结果作答；也可以接远端
`rwkv_lightning` 部署或任意 OpenAI 兼容接口。

- **零 Python 运行时**：Go 负责 Conversation、Session 与 Agent 事务；推理由独立的
  `librwkv_agent_runtime.dylib`（固定版本的 RWKV Mobile tokenizer/sampler + MLX FFI）完成，
  不依赖 PyTorch、HTTP 服务或外部进程。
- **一套 API，四种入口**：CLI、TUI、桌面 App、浏览器服务共用同一个公开 `api` 包。
- **自带评测台**：`agent-eval` 内置多套 suite，每次运行产出可复现的 run/trace/summary；
  `rwkv-lab` 负责题库、语料与跑分流水线。

[English version](README.en.md) · [项目总索引](INDEX.md) · [CLI 参考手册](docs/guides/cli.md)

## 当前状态

| 方面 | 状态 |
| --- | --- |
| 平台 | Apple Silicon、macOS 15+ 源码构建可用。Linux 仅在 CI 验证 `-tags server`（远程 provider）；Windows 暂无入口 |
| 产品形态 | CLI / TUI、Wails V3 桌面 App、headless 浏览器服务 |
| Agent | 实验性；工具只读，不写文件、不执行命令。评测 Harness 版本 `rwkv-agent-eval-v22` |
| 分发 | 技术链路已通；公开分发前需确认上游授权并选定项目许可证 |

## 快速开始

> 第一次使用建议直接照 [macOS 从零上手](docs/guides/getting-started-macos.md) 走一遍，
> 里面有模型准备、更新和常见报错。

**环境**：Apple Silicon Mac（macOS 15+）、Xcode（含 Swift 与 Metal Toolchain）、
CMake 3.25+、Ninja、Go 1.26+；构建桌面 App 另需 Node.js 26（pnpm 由脚本自动准备）。
模型用 RWKV-7 `.pth` checkpoint，或已转换的 MLX safetensors 目录。

```sh
git submodule update --init --recursive
brew install cmake ninja go

./scripts/build-macos.sh --check   # 检查环境
./scripts/build-macos.sh           # 产物在 local/dist/
```

**和模型对话**（直接加载 `.pth`，无需转换）：

```sh
./local/dist/rwkv-cli run \
  --model /absolute/path/to/rwkv7-model.pth \
  --session ./local/sessions/demo.rwkv-session --autosave
```

**让 Agent 读你的项目**：

```sh
./local/dist/rwkv-cli agent \
  --model /absolute/path/to/rwkv7-model.pth \
  --workspace /absolute/path/to/project \
  --prompt "阅读 README 和 docs，概括当前已完成内容与下一步"
```

**桌面 App**：

```sh
./scripts/build-app.sh
open -n "./local/dist/RWKV Agent.app" --args --workspace "$(pwd)"

# 不开窗口，只起浏览器服务
./local/dist/rwkv-app-server --host 127.0.0.1 --port 8080
```

## 组成

| 入口 | 做什么 |
| --- | --- |
| `rwkv-cli run` | 单轮生成或多轮 REPL；Session 可保存、恢复 |
| `rwkv-cli agent` | 工作区 Agent，交互终端进全屏 TUI，脚本/pipe 自动纯文本 |
| `rwkv-cli agent-eval` | 固定题集评测，输出 `run.json` / `trace.jsonl` / `summary.json` |
| `rwkv-cli concurrent` · `bench` | 单模型 1–8 路并发生成 dashboard，可点选某一路继续追问 |
| `rwkv-cli convert` | `.pth` → MLX safetensors（不依赖 Python，可选） |
| `rwkv-cli state` | 向 `rwkv_lightning` 部署上传 / 列出 / 删除 State |
| 桌面 App（`cmd/rwkv-app`） | 本地或远端模型配置、持久会话、工具轨迹、流式回答、State 管理 |
| `rwkv-lab`（`cmd/rwkv-lab`） | 开发工具：`bank` 题库、`corpus` 语料渲染、`run` 检查与对比、`bench` 扫描、`state` 训练辅助 |

每个命令的完整参数和行为细节见 [CLI 参考手册](docs/guides/cli.md)；App 的存储与配置见
[docs/guides/app.md](docs/guides/app.md)。

## 核心能力

**推理**

- 直接 mmap `.pth` 装入 MLX，不写第二份权重；首次加载生成几十到几百 KB 的元数据索引，
  checkpoint 变化后自动重建。
- 单模型 scheduler + continuous batching，最多 8 路活跃 Session，各自的采样器与 State 隔离。
- 默认采用 G1 官方聊天模板；`--thinking off|fast|full` 控制思考预填充。

**会话**

- Session 由不可变 revision 和原子 `CURRENT` 指针组成，transcript 是事实源，`state.bin`
  只是带校验的加速快照，缺失或不兼容时自动 replay。
- 每轮先在候选 transcript 上生成，完整成功才提交；取消或出错不会留下半截消息。

**Agent**

- 默认工具：工作区内列目录、读文件、字面量搜索，以及 `calculator`、`data_query`、`datetime`。
- 可选：`--web` 开启 Brave 搜索 + Tavily 抓取（429/5xx 自动退避重试）；`--subagents` 开启
  `spawn_agents`，一次并发 2–8 个独立子任务，子 Agent 不能再派生。
- 安全边界：所有路径限定在 `--workspace` 内，拒绝绝对路径、`..` 穿越和越界符号链接；
  单文件读取上限 64 KiB。整轮成功后才事务化提交，失败整轮回滚。
- 工具调用格式（XML / Markdown / G1K 等）由独立的 wire 层描述，可用 `--profile` 切换，
  见 [Wire 配置指南](docs/guides/wire-configuration.md) 与
  [工具与对话格式总览](docs/design/tool-and-wire-formats.md)。

**远程 Provider**

| `--completion` | 后端 |
| --- | --- |
| `local` | 本地 MLX 推理（默认） |
| `rwkv-lightning-cuda` | C++/CUDA Lightning，`/v1/batch/completions` 原始续写，支持 `--state-id` 复用上传的 State |
| `rwkv-lightning-python` | Python Lightning，`/v1/chat/completions` 原始续写 |
| `chat-completions` | OpenAI 兼容 Chat Completions，需 `-tags chatcompletions` 或 `build-macos.sh --with-chat-completions` |

凭证只从环境变量读取（`--api-key-env`、`--api-header-env HEADER=ENV`），不进入命令行参数、
配置文件或评测产物。示例与各后端差异见 [CLI 参考手册 · 远程 Provider](docs/guides/cli.md#5-远程-provider)。

## 评测

```sh
./local/dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite boundary \
  --output local/runs/local-boundary
```

| 题集 | 内容 |
| --- | --- |
| workbank（`--cases bench/workbank/cases`） | **主考卷**：148 道真实 Agent 任务，每题带 `verify.py` 判分 |
| `bfcl-product` | 60 道从 BFCL 语义转化的产品题：主动不调用、缺参追问、多轮决策 |
| `boundary`（默认） | 18 道改造自 primitive-bench 的只读任务 |
| `smoke` / `assistant` | 协议与安全契约回归；天气、交通、汇率等 mock 工具场景 |
| `primitive-orig30` / `primitive-feedback30` | 内嵌的 Primitive Bench 固定快照 |

正式跑分请遵循 [跑分规程](docs/evaluations/benchmark-protocol.md)（格式、预算、采样预设、
并发上限与 `rwkv-lab run check` 闸门）。历次结果与结论在
[docs/evaluations/](docs/evaluations/)，不同 Harness 版本或题库版本的分数不可直接比较。

## 测试

```sh
go test ./...                       # 不需要真实模型
go test -race ./...
./scripts/test-macos-native.sh      # C ABI 生命周期 + AddressSanitizer

RWKV_TEST_PTH=/absolute/path/to/rwkv7-model.pth ./scripts/test-macos-real-model.sh
```

CI（`.github/workflows/ci.yml`）跑 Go race 测试、Linux `-tags server` 构建与 vet，以及前端
`pnpm test` + `pnpm build`。

## 项目结构

```text
api/                     CLI / TUI / App / 浏览器服务共用的公开 Agent API
cmd/
  rwkv-cli/              CLI 与 TUI 入口
  rwkv-app/              Wails V3 桌面 App（Go 后端 + React 前端）
  rwkv-lab/              题库、语料、跑分开发工具
internal/
  agent/                 Agent Harness、wire 层、工具实现；agent/eval/ 为评测 suite
  continuation/          生成器抽象与 local / rwkvlightning / chatcompletions 适配
  conversation/          transcript、revision 与 session bundle
  inference/  native/    推理核心、调度与 MLX FFI / converter
  lab/                   rwkv-lab 各子命令的实现
  cli/  tui/  appstorage/ …
native/                  C ABI runtime（librwkv_agent_runtime）
bench/                   入库数据：workbank 与蒸馏题库、老师脚本、冻结基线（见 bench/README.md）
docs/                    文档：guides/ 使用、design/ 设计与契约、evaluations/ 评测、distill/ 蒸馏、archive/ 停更
scripts/                 构建、测试、BFCL 脚本
third_party/rwkv-mobile  固定 revision 的 tokenizer/sampler 上游（submodule）
local/                   本机产物（构建、模型、runs），不入库
```

## 文档导航

| 想找什么 | 去哪看 |
| --- | --- |
| 从零上手、常见问题 | [getting-started-macos.md](docs/guides/getting-started-macos.md) |
| 每个命令的完整参数 | [cli.md](docs/guides/cli.md) |
| 桌面 App 与公开 API | [app.md](docs/guides/app.md) |
| 工具调用格式与 wire 配置 | [tool-and-wire-formats.md](docs/design/tool-and-wire-formats.md) · [wire-configuration.md](docs/guides/wire-configuration.md) |
| 推理核心与 `.pth` 直读设计 | [inference-core-design.md](docs/design/inference-core-design.md) · [direct-pth-loading.md](docs/design/direct-pth-loading.md) |
| 续写接口与 Agent 协议 | [continuation-and-agent-protocol.md](docs/design/continuation-and-agent-protocol.md) |
| 跑分规程与评测结论 | [benchmark-protocol.md](docs/evaluations/benchmark-protocol.md) · [docs/evaluations/](docs/evaluations/) |
| 蒸馏语料流程 | [distill-workflow.md](bench/distill/common/distill-workflow.md) |
| 数据放在哪 | [bench/README.md](bench/README.md) |
| 全部文档 | [INDEX.md](INDEX.md) · [docs/README.md](docs/README.md) |

## 许可证

当前固定的 `rwkv-mobile` revision 根目录没有明确的 LICENSE 文件。公开分发前仍需确认上游
源码、MLX Swift FFI 及其依赖的授权条件，并为 RWKV-Agent 选定项目许可证。
