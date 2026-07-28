# RWKV-Agent

跨平台 RWKV Agent 软件。Go 负责 Agent Harness、桌面宿主与系统集成，UI 计划使用 WebAssembly 并运行在系统 WebView 中。模型推理必须是可随应用分发的原生实现，不使用 Python 后端。

推理核心的跨平台接口、Session、Capability 和 RWKV State 语义见
[`docs/inference-core-design.md`](docs/inference-core-design.md)。

当前最小可运行版本使用 [`rwkv-mobile`](https://github.com/MollySophia/rwkv-mobile) 的 C++ Runtime 和 MLX 后端：

```text
Go CLI → cgo → rwkv-mobile C API → C++ MLX backend → Metal
```

仓库把 `rwkv-mobile` 固定为 Git submodule。Apple Silicon 构建只启用 MLX；llama.cpp、Core ML、MNN、NCNN、WebRWKV 和 HTTP Server 均不参与这一构建。

## 环境

- Apple Silicon Mac
- Xcode（包含 Swift toolchain）
- CMake 3.25+
- Ninja
- Go 1.26+
- 上游发布的 RWKV-7 `.pth` 权重，或已经转换好的 MLX 模型目录

## 构建

首次拉取后初始化上游依赖：

```sh
git submodule update --init --recursive
```

构建 C++ MLX Runtime、Metal 资源和 Go CLI：

```sh
./scripts/build-mlx.sh
```

产物位于 `dist/`：

```text
dist/
├── rwkv-cli
├── librwkv_mobile.dylib
├── assets/
│   └── rwkv_vocab_v20230424.txt
└── mlx-swift_Cmlx.bundle/
    └── Contents/Resources/default.metallib
```

动态库和 Metal resource bundle 都是运行时必需文件，分发时必须和 CLI 一起携带。以后打包 `.app` 时，它们应分别进入 Frameworks 和 Resources。

## 转换模型

上游 RWKV 发布的 `.pth` 需要先转换一次。转换器已经编译进 `rwkv-cli`，它直接在 C++ 中读取 PyTorch checkpoint 并输出 MLX 所需的 safetensors，不依赖 Python、PyTorch 或外部转换进程：

```sh
./dist/rwkv-cli convert \
  --input /absolute/path/to/rwkv7-model.pth \
  --output /absolute/path/to/rwkv7-model-mlx
```

默认输出 BF16，并自动携带 RWKV World tokenizer。输出目录包含：

```text
rwkv7-model-mlx/
├── config.json
├── model.safetensors
└── rwkv_vocab_v20230424.txt
```

可以通过 `--precision fp16` 或 `--precision fp32` 更改输出精度。目标目录已存在时转换器默认拒绝覆盖；确认替换可加 `--overwrite`，替换过程使用同目录临时目录和原子重命名，失败时保留原输出。

目前转换器针对 RWKV-7 官方 checkpoint 的键名和张量布局；不把任意 PyTorch 模型伪装成 RWKV 模型。

## 运行

使用模型目录内的默认 tokenizer：

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/mlx-model-directory \
  --prompt "你好，请介绍一下你自己。" \
  --max-tokens 128
```

也可以显式指定 tokenizer：

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/mlx-model-directory \
  --tokenizer /absolute/path/to/rwkv_vocab_v20230424.txt \
  --prompt "你好"
```

省略 `--prompt` 会加载一次模型并进入交互模式。默认按 RWKV G1 的 chat 模板渲染用户输入，并使用 fast-thinking 标记；普通非 reasoning 模型可传 `--reasoning=false`。如需对原始文本做续写，传 `--raw`。

## 测试

普通 Go 测试不要求本机已有原生构建：

```sh
go test ./...
```

构建 MLX Runtime 后，可执行真实模型集成测试：

```sh
RWKV_TEST_MODEL=/absolute/path/to/mlx-model-directory \
RWKV_TEST_TOKENIZER=/absolute/path/to/rwkv_vocab_v20230424.txt \
./scripts/test-mlx.sh
```

转换器也提供可选的实模回归测试；如果设置参考 safetensors，还会执行 SHA-256 一致性校验：

```sh
RWKV_TEST_PTH=/absolute/path/to/model.pth \
RWKV_TEST_TOKENIZER=/absolute/path/to/rwkv_vocab_v20230424.txt \
RWKV_TEST_CONVERTER_REFERENCE=/absolute/path/to/reference/model.safetensors \
go test -tags converter ./internal/native/converter -run TestNativeConversion -v
```

运行时不加载 Python，也不启动外部推理进程或 HTTP Server。

## 分发注意

当前固定的 `rwkv-mobile` revision 没有在仓库根目录提供明确的 LICENSE 文件。技术打包链已经可用，但公开分发前仍需确认上游源码及其预编译 `libMLXModelFFI.a` 的授权条件，并为 RWKV-Agent 选择自己的项目许可证。
