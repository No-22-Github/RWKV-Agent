# rwkv-cli

最小的 Go 命令行胶水层：启动 `rwkv-mobile` 的 `rwkv_server`、等待模型加载完成，然后把续写的流式输出直接写到终端。

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
