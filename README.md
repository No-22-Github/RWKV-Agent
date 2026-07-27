# rwkv-cli

最小的 Go 命令行胶水层：启动 `rwkv-mobile` 的 `rwkv_server`、等待模型加载完成，然后把续写的流式输出直接写到终端。

## 先构建运行时

在 `rwkv-mobile` 源码目录中构建最小 CPU/Metal 可用组合（实际后端取决于模型格式）：

```sh
cmake -S . -B build -DBUILD_EXAMPLES=ON -DENABLE_SERVER=ON
cmake --build build --target rwkv_server -j
```

## 构建并运行 CLI

```sh
go build -o rwkv-cli ./cmd/rwkv-cli
./rwkv-cli run \
  --engine /absolute/path/to/rwkv_server \
  --model /absolute/path/to/model \
  --tokenizer /absolute/path/to/tokenizer \
  --backend web_rwkv
```

省略 `--prompt` 后进入交互式续写模式；也可以一次性续写：

```sh
./rwkv-cli run --engine /path/rwkv_server --model /path/model --tokenizer /path/tokenizer --backend web_rwkv --prompt 'Once upon a time'
```

如果运行时已经独立启动，使用 `complete`：

```sh
./rwkv-cli complete --url http://127.0.0.1:8000 --prompt 'Once upon a time'
```

`--backend` 必须与所下载模型的格式相匹配；上游支持的名称和兼容组合由其构建配置决定。
