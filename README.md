# RWKV-Agent

RWKV-Agent 当前提供一个可分发的 Apple Silicon macOS 本地 CLI。Go 负责 Conversation 事务、Session 持久化和终端交互；独立的 `librwkv_agent_runtime.dylib` 通过固定版本的 RWKV Mobile tokenizer/sampler 与 MLX FFI 执行推理。运行时不依赖 Python、PyTorch、HTTP 服务或外部进程。

```text
rwkv-cli
  → Conversation（transcript / revision / rollback / replay）
  → inference backend
  → versioned C ABI + per-request callback
  → single-model scheduler
  → MLX continuous batch（最多 4 个活跃 Session）
```

详细设计和验收范围见：

- [`docs/inference-core-design.md`](docs/inference-core-design.md)
- [`docs/rwkv-mobile-adoption-and-cli-milestone.md`](docs/rwkv-mobile-adoption-and-cli-milestone.md)
- [`docs/rwkv-mobile-macos-cli-implementation-plan.md`](docs/rwkv-mobile-macos-cli-implementation-plan.md)
- [`docs/rwkv-cli-tui-redesign-plan.md`](docs/rwkv-cli-tui-redesign-plan.md)

## 环境

- Apple Silicon Mac
- macOS 15+
- Xcode（包含 Swift toolchain）
- CMake 3.25+
- Ninja
- Go 1.26+
- RWKV-7 `.pth` checkpoint，或已转换的 MLX safetensors 模型目录

首次拉取后初始化固定版本的上游依赖：

```sh
git submodule update --init --recursive
```

## 构建

```sh
./scripts/build-macos.sh
```

构建脚本固定 `arm64` 和 `MACOSX_DEPLOYMENT_TARGET=15.0`，并验证 dylib、rpath、Metal resource、deployment target 和 CLI help smoke test。产物如下：

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

## 转换 `.pth`

转换器直接读取 PyTorch ZIP/pickle checkpoint 并写出 MLX safetensors，不加载 Python 或 PyTorch：

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
  --model /absolute/path/to/rwkv7-model-mlx \
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

transcript 是事实源，`state.bin` 只是带 codec、尺寸、prefix token 和 checksum 校验的 MLX State 加速快照。快照不存在或导入失败时会自动 replay transcript；模型、tokenizer、prompt profile 或 Initial State 指纹不兼容时拒绝加载。`/load` 使用临时 Conversation 完成校验和恢复，成功后才替换当前会话。

## 4 路并发

`concurrent` 命令用一个模型实例创建多个 Session，并让 native scheduler 合并单 token decode：

```sh
./dist/rwkv-cli concurrent \
  --model /absolute/path/to/rwkv7-model-mlx \
  --concurrency 4 \
  --max-tokens 64 \
  --concurrent-prompt "用一句话介绍 RWKV"
```

输出会报告 `max_native_batch`。目标配置中它应达到 4，且每个 Session 的 callback、采样器、token、取消标志和 State 都彼此隔离。MLX FFI 支持 16 个物理 State slot；当前交付把业务活跃 batch 上限固定为 4，并为额外请求提供有界 FIFO 队列。

## 测试

不依赖真实模型：

```sh
go test ./...
go test -race ./...
./scripts/test-macos-native.sh
```

`test-macos-native.sh` 还会构建 AddressSanitizer 版本并运行 C ABI lifecycle test。

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

真实模型脚本覆盖转换、单轮生成、4 路 concurrent batch、保存、native State 恢复，以及移除 `state.bin` 后的 transcript replay。

## 分发注意

当前固定的 `rwkv-mobile` revision 没有在仓库根目录提供明确的 LICENSE 文件。技术打包链已经可用，但公开分发前仍需确认上游源码及预编译 `libMLXModelFFI.a` 的授权条件，并为 RWKV-Agent 选择项目许可证。
