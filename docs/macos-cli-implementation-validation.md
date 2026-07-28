# macOS CLI 实施与验证记录

日期：2026-07-28

对应计划：

- [`rwkv-mobile-macos-cli-implementation-plan.md`](rwkv-mobile-macos-cli-implementation-plan.md)
- [`rwkv-cli-tui-redesign-plan.md`](rwkv-cli-tui-redesign-plan.md)

## 已落地范围

- `rwkv_agent_runtime` C ABI v1、opaque Runtime/Model/Session handle 和稳定错误码。
- 同步 load/prefill/generate、`request_id + user_data` callback、跨线程 cancel，以及 close/cancel/wait 生命周期。
- 精确 token encode、prefix 同步、dirty/rebuild 状态和 FNV64 native prefix hash。
- MLX fp16 recurrent cache、prefix token IDs 和 logits 的 native State codec。
- Go `runtime/cgo.Handle` callback 路由；旧的进程级 writer 和 generation mutex 路径已删除。
- 版本化 `rwkv-g1-chat` prompt profile（当前为 v2，遵循官方 G1 QA/快速思考模板且不注入字面量伪 BOS）。
- Conversation candidate turn、失败回滚、canonical transcript hash 和 SHA-256 logical revision。
- 不可变 Session revision、原子 `CURRENT`、checksum、兼容性校验和 logical-only replay。
- `/state`、`/history`、`/save`、`/load`、`/reset`、`/new`、`/help`、`/exit`。
- per-turn `Ctrl-C` 取消和 idle `Ctrl-C` 退出。
- 单模型 scheduler、最多 8 个活跃 Session slot、continuous batch、独立 callback/sampler/cancel/State 和有界 FIFO。
- macOS 15.0 deployment target、`@executable_path` rpath、Metal bundle 和 build manifest。
- Bubble Tea v2 concurrent dashboard、Lip Gloss v2 响应式布局和共享 CLI theme。
- UI 无关 concurrent runner、统一 snapshot/summary、dirty 合并和 context 全局取消。
- `--ui auto|tui|plain`、非 TTY/CI/`TERM=dumb` 自动降级和 plain 无 ANSI 契约。
- 4×2、2×4、2×2、双列、单列和 compact pane；CJK/emoji cell 宽度、鼠标点选、
  选中 Conversation 续聊、滚动、复制和 rerun。

内部 fork 的维护目标通过主仓库内的独立 facade 实现：facade 直接链接固定 submodule revision 中的 tokenizer/sampler 和 MLX FFI，不修改 submodule，也不依赖不可获取的外部 fork commit。submodule 仍固定在 `a9a66e8bea2a708d6ca14ccb9bb46c721a5b7fdd`。

## 指定模型

输入 checkpoint：

```text
/Users/no22/Projects/Preen/models/rwkv7-g1h-1.5b-20260710-ctx10240.pth
```

本机转换结果：

```text
build/real-model-test/model-mlx/
├── config.json
├── model.safetensors
└── rwkv_vocab_v20230424.txt
```

转换器识别结果：

```text
RWKV-7
layers=24
hidden=2048
vocab=65536
tensors=795
```

## 实机结果

### 构建产物

`./scripts/build-macos.sh` 通过。`vtool -show-build` 对 CLI 和 dylib 均报告：

```text
platform MACOS
minos 15.0
```

`otool -L dist/rwkv-cli` 报告：

```text
@rpath/librwkv_agent_runtime.dylib
```

### 单轮与五轮

- 指定模型成功加载并完成流式单轮生成。
- 同一 REPL 连续完成五个 turn。
- `/history` 显示 10 条已提交 user/assistant 消息。
- `/state` 显示 `status=clean`、10 条消息对应的完整 committed prefix token 数和 native prefix hash。

### State 保存与恢复

- `/save` 写出 manifest、JSONL transcript 和 `state.bin`。
- 重新启动后通过 native snapshot 恢复，`/state` 显示 `recovery=native`。
- 将 `state.bin` 移出当前 revision 后重新启动，CLI replay 72 个 transcript token，显示 `recovery=replay`。
- native snapshot 和 replay 得到相同 prefix token 数与 native prefix hash。
- v1 prompt profile Session 启动时继承原 reasoning 模式，验证旧 logical revision 后丢弃旧
  native State，以 v2 replay transcript，并显示 `recovery=profile-migration`；autosave
  写入新的不可变 v2 revision。

### Ctrl-C

- 在 512 token 长生成期间发送第一次 `Ctrl-C`。
- CLI 输出取消提示，返回 REPL prompt，并明确报告 committed transcript 未变化。
- 空闲 prompt 再发送 `Ctrl-C`，进程正常退出。

### 4 路 continuous batch

命令：

```sh
./dist/rwkv-cli concurrent \
  --model build/real-model-test/model-mlx \
  --tokenizer dist/assets/rwkv_vocab_v20230424.txt \
  --concurrency 4 \
  --max-tokens 8 \
  --reasoning=false
```

结果：

```text
sessions=4
max_native_batch=4
tokens=31
aggregate=29.9 tok/s
```

真实模型 integration test 还覆盖了：4 个请求重叠后取消其中一个；被取消 Session 为 `dirty` 且不提交，另外 3 个 Session 保持 `clean`、输出非空且成功提交，native instrumentation 的最大 batch 为 4。

### 8 路 State 隔离与动态入队

发现并修复了一个原生层 State 槽位污染：scheduler 已有活跃 decode 请求时，新请求的
scalar prefill 会临时使用 MLX slot 0；旧实现只保存和恢复 slot 0，prefill 过程中却可能
改写其他活跃物理 slot，导致相同的“你好”偏移到无关语言。

修复后，scalar prefill 会在持有 compute lock 时保存并恢复 `[0, active_count)` 的全部
活跃 slot。真实模型 integration test 先启动 2 个 decode，再动态加入 6 个请求，使用
`top-k=1` 验证 8 个完整输出逐字相同，并确认：

```text
sessions=8
max_native_batch=8
tokens=128
elapsed=2.756s
aggregate=46.4 tok/s
state-slot outputs=identical
```

普通采样仍为每个 Session 使用独立 seed，因此措辞可以不同；解码参数在各窗口间保持一致。

### CLI/TUI 重做验收

使用 `build/real-model-test/model-mlx` 的结果：

```text
single turn:
prefill=102.7 tok/s
decode=25.6 tok/s

concurrency=1:
max_native_batch=1

concurrency=2:
max_native_batch=2

concurrency=4, max-tokens=256:
max_native_batch=4
tokens=784
elapsed=10.247s
aggregate=76.5 tok/s
```

相同四路短 prompt、`max-tokens=32` 的三次中位数：

```text
plain median aggregate=63.0 tok/s
TUI median aggregate=63.5 tok/s
relative change=+0.8%
```

达到“TUI 相对 plain 回退不超过 5%”门槛。真实 PTY 中验证了 120×32 的 2×2 dashboard、
实时 `native batch 4/4`、完成后选中 pane 续聊和 alternate-screen 恢复。运行中发送 `q`
得到：

```text
Concurrent batch cancelled: sessions=4 max_native_batch=4 tokens=88 elapsed=1.137s aggregate=77.4 tok/s
```

四路取消后进程正常退出且终端恢复。自动 PTY 测试同时覆盖 resize 到 80×24、正常完成、
SGR 鼠标点击 pane、在同一 Conversation 内继续提问、续聊取消回滚、`q` 全局取消以及
`\x1b[?1049h` / `\x1b[?1049l` 成对恢复。真实模型也验证了 8 路完成后点击 Session 3，
追问答案继续流入 Session 3，native 最大 batch 仍为 8。

## 自动化门禁

以下命令通过：

```sh
go test ./...
go test -race ./...
./scripts/test-macos-native.sh
```

`test-macos-native.sh` 包括普通 Go tests、race tests、带 `mlx` tag 的 adapter tests，以及 AddressSanitizer C ABI lifecycle test。

真实模型入口：

```sh
RWKV_TEST_PTH=/Users/no22/Projects/Preen/models/rwkv7-g1h-1.5b-20260710-ctx10240.pth \
./scripts/test-macos-real-model.sh
```
