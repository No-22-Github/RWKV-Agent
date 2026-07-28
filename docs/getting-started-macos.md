# macOS 从零上手

这份文档面向第一次拿到 RWKV-Agent 仓库、希望尽快在本地跑起聊天的人。

当前可用实现是 **Apple Silicon macOS 15+**。Windows 和 Linux 属于项目目标，但还没有
可用的构建与运行入口。模型权重不包含在仓库中，需要自行准备 RWKV-7 G1 的 `.pth`
checkpoint，或已经转换好的 MLX 模型目录。

## 1. 安装构建环境

需要完整 Xcode，而不只是 Command Line Tools。先从 App Store 或 Apple Developer
安装并启动一次 Xcode，然后安装其余工具：

```sh
brew install cmake ninja go
```

如果电脑上装了多个 Xcode，确保命令行选择的是完整 Xcode：

```sh
xcode-select -p
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

项目当前要求：

- Apple Silicon Mac（`arm64`）
- macOS 15 或更新版本
- 完整 Xcode，包含 macOS SDK、Swift 和 Metal Toolchain
- CMake 3.25+
- Ninja
- Go 1.26+
- Git

## 2. 获取源码

新克隆建议直接带上 submodule：

```sh
git clone --recurse-submodules https://github.com/No-22-Github/RWKV-Agent.git
cd RWKV-Agent
```

如果已经克隆过仓库，补齐固定版本的依赖：

```sh
git submodule update --init --recursive
```

## 3. 检查并构建

先做一次不编译的环境检查：

```sh
./scripts/build-macos.sh --check
```

检查通过后构建：

```sh
./scripts/build-macos.sh
```

脚本会依次准备固定版本的 MLX Swift bridge、编译原生运行时、编译 Go CLI，并检查最终
包的动态库路径、最低系统版本和 Metal resource。缺少 `rwkv-mobile` submodule 时，正常
构建会自动初始化它。

第一次构建需要从网络拉取 MLX Swift 依赖，耗时会明显长于后续构建。成功后可执行文件是：

```text
dist/rwkv-cli
```

请保留整个 `dist/` 目录，不要只复制 `rwkv-cli`。程序运行时还需要同目录中的 dylib、
tokenizer 和 Metal resource。

## 4. 准备模型

最省事的方式是直接使用 RWKV-7 `.pth`：

```sh
RWKV_MODEL=/absolute/path/to/rwkv7-model.pth
```

路径最好使用绝对路径；包含空格时记得加引号。直接加载不会生成第二份完整模型，只会在
`~/Library/Caches/RWKV-Agent/pth-index/v1/` 保存一个很小的 checkpoint 索引。

也可以使用 `rwkv-cli convert` 预先转换成 MLX 目录：

```sh
./dist/rwkv-cli convert \
  --input "$RWKV_MODEL" \
  --output /absolute/path/to/rwkv7-model-mlx
```

## 5. 开始聊天

先用单轮命令验证模型能正常加载：

```sh
./dist/rwkv-cli run \
  --model "$RWKV_MODEL" \
  --prompt "你好，请用一句话介绍你自己。" \
  --max-tokens 128
```

进入多轮聊天并自动保存 Session：

```sh
./dist/rwkv-cli run \
  --model "$RWKV_MODEL" \
  --session ./sessions/demo.rwkv-session \
  --autosave
```

REPL 中常用命令：

```text
/state          查看当前会话和 native State 状态
/history        查看已提交的对话
/save [path]    保存 Session
/load <path>    加载 Session
/reset          清空当前对话
/help           查看帮助
/exit           退出
```

普通聊天使用 RWKV G1 官方 `User: ... / Assistant:` 模板。需要快速思考模板时显式加入
`--reasoning`；不要在问题中手写 `<|bos|>`。

## 6. 并发生成

下面的命令让一个模型实例同时运行四个独立 Session：

```sh
./dist/rwkv-cli concurrent \
  --model "$RWKV_MODEL" \
  --concurrency 4 \
  --concurrent-prompt "用一句话介绍 RWKV" \
  --max-tokens 128
```

在交互终端中默认打开实时 dashboard；用于 CI、重定向或复制稳定文本时使用
`--ui plain`。并发上限当前是 8。

## 7. 更新项目

拉取新代码后，一般直接更新 submodule 并重新构建即可：

```sh
git pull --ff-only
git submodule update --init --recursive
./scripts/build-macos.sh
```

`build/` 是生成缓存，`dist/` 是可运行产物。重新构建不会删除 Session 或模型。

## 常见问题

### `patch does not apply`

旧版构建脚本没有按仓库中补丁的零上下文格式调用 `git apply`，因此首次构建或遇到只应用
了一部分的旧缓存时都可能出现：

```text
error: patch failed: Tools/MLXModelFFI/MLXModelFFI.swift:52
error: ... patch does not apply
```

最新脚本会按正确格式应用补丁，并自动修复旧的生成缓存。先拉取最新代码，再重新运行：

```sh
git pull --ff-only
./scripts/build-macos.sh
```

如果该目录被手动改得无法恢复，可以把生成缓存移走后重试：

```sh
mv build/mlx-swift-source build/mlx-swift-source.backup
./scripts/build-macos.sh
```

这不会影响模型、Session 或项目源码。

### `Missing build tools`

安装命令行依赖：

```sh
brew install cmake ninja go
```

`xcodebuild`、`swift`、`xcrun`、`otool` 或 `metal` 缺失时，需要安装完整 Xcode，并用
`xcode-select` 选中它。

### `rwkv-mobile is not initialized`

环境检查不会改动仓库，因此会提示手动初始化：

```sh
git submodule update --init --recursive
```

直接运行正式构建时，脚本会尝试自动完成这一步。

### Swift package 下载失败

首次构建依赖网络。如果是临时网络或 GitHub 连接错误，直接重新运行构建即可，已经完成的
下载和编译会复用缓存。

### `Library not loaded: @rpath/librwkv_agent_runtime.dylib`

不要把二进制单独移出 `dist/`。从项目目录运行 `./dist/rwkv-cli`，或完整复制整个
`dist/` 目录。

### 模型加载失败

先确认：

- 传入的是 RWKV-7 `.pth` 文件或 `rwkv-cli convert` 生成的 MLX 目录；
- 路径存在，并且使用了绝对路径或正确的引号；
- 磁盘有足够空间，内存能够容纳模型；
- 自定义 vocabulary 的模型同时传入了匹配的 `--tokenizer`。

还不能定位时，保留完整错误输出，并附上以下信息：

```sh
./scripts/build-macos.sh --check
./dist/rwkv-cli --help
```
