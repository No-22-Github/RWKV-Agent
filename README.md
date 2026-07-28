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
--reasoning
--autosave
--native-state auto|off|required
```

默认使用 RWKV 官方 G1 常规聊天模板 `User: ...\n\nAssistant:`。难题可额外传入
`--reasoning`，启用官方快速思考模板 `Assistant: <think>\n</think>`；不要把
`<|bos|>` 等伪 special token 写进 prompt。

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
revision，丢弃旧版 native State，再用当前 profile replay。未显式传 `--reasoning` 时会
继承 Session 原有的 reasoning 模式；显式模式冲突、模型或 tokenizer 不匹配仍会拒绝。
迁移后的 autosave 写入新 revision，不会原地改写旧 revision。

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
