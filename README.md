# RWKV-Agent

跨平台 RWKV Agent 软件。计划以 Go 实现 Agent Harness、桌面端和系统集成，UI 使用 WebAssembly 并运行在系统 WebView 中。

仓库目前处于最小可运行阶段，只包含 `rwkv-cli`：它可以启动
[`rwkv-mobile`](https://github.com/MollySophia/rwkv-mobile) 的 `rwkv_server`、等待模型加载完成，然后把流式续写直接写到终端；也可以通过 llama.cpp 的 Metal 后端直接加载 RWKV GGUF 模型。Desktop 和 WASM UI 尚未开始实现。

## 先构建运行时

本项目第一版在 Apple Silicon 上固定使用上游的 **Core ML** 后端，以利用 Apple Neural Engine。构建时只启用它：

```sh
cmake -S . -B build \
  -DBUILD_EXAMPLES=ON -DENABLE_SERVER=ON \
  -DENABLE_COREML_BACKEND=ON \
  -DENABLE_WEBRWKV_BACKEND=OFF -DENABLE_NCNN_BACKEND=OFF \
  -DENABLE_LLAMACPP_BACKEND=OFF -DENABLE_MNN_BACKEND=OFF \
  -DENABLE_MLX_BACKEND=OFF
cmake --build build --target rwkv_server -j
```

## 构建并运行 CLI

```sh
go build -o rwkv-cli ./cmd/rwkv-cli
./rwkv-cli run \
  --engine /absolute/path/to/rwkv_server \
  --model /absolute/path/to/coreml-model-directory \
  --tokenizer /absolute/path/to/tokenizer \
  --backend coreml
```

省略 `--prompt` 后进入交互式续写模式；也可以一次性续写：

```sh
./rwkv-cli run --engine /path/rwkv_server --model /path/coreml-model-directory --tokenizer /path/tokenizer --backend coreml --prompt 'Once upon a time'
```

如果运行时已经独立启动，使用 `complete`：

```sh
./rwkv-cli complete --url http://127.0.0.1:8000 --prompt 'Once upon a time'
```

Core ML 的输入不是原始 `.pth` 文件。上游转换脚本会从 `.pth` 权重生成一个模型目录，其中包含 `config.yaml` 和一个或多个由 Xcode 编译出的 `.mlmodelc` 目录；把这个模型目录传给 `--model`。分词器仍使用与原始 RWKV 权重匹配的 tokenizer 文件。

## 已验证的 Apple Silicon 最小路径

当前 macOS 的 Core ML 运行时无法加载上游转换器产生的多入口模型，因此最小可用入口改为已验证的 llama.cpp Metal 路径。它使用 Apple GPU，并可直接加载 RWKV 的 `.gguf` 文件，无须转换。

```sh
./rwkv-cli llama \
  --engine /Users/no22/Projects/Preen/models/llama-b9939/llama-cli \
  --model /Users/no22/Projects/Preen/models/rwkv7-g1g-1.5b-20260526-ctx8192-FP16.gguf \
  --prompt 'The capital of France is' \
  --max-tokens 64
```

省略 `--prompt` 会进入交互模式。
