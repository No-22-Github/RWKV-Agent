# RWKV Mobile macOS CLI 完整实施计划

状态：Implemented（Implementation Plan v1.0）

分析日期：2026-07-28

目标平台：macOS 15+ / Apple Silicon

上游基线：RWKV Mobile `a9a66e8bea2a708d6ca14ccb9bb46c721a5b7fdd`

关联文档：

- [RWKV Mobile 采用方案与 CLI 多轮对话里程碑](rwkv-mobile-adoption-and-cli-milestone.md)
- [跨平台推理核心设计](inference-core-design.md)
- [macOS CLI 实施与验证记录](macos-cli-implementation-validation.md)

实施说明：功能里程碑 PR 0–8 已在主分支方案中整体落地；当前交付按本机目标将 active continuous batch 配置为 4。内部 fork 目标通过主仓库内独立、版本化的 native facade 实现，固定 submodule 本身保持不修改，详见验证记录。

## 1. 最终交付结果

第一阶段交付一个不依赖 Python 和外部服务的本地命令行程序：

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/rwkv-mlx-model \
  --session ./sessions/demo.rwkv-session
```

它必须支持：

1. 在 Apple Silicon Mac 上通过 RWKV Mobile 的 MLX provider 加载本地模型。
2. 在同一个 REPL 中进行至少五轮有上下文的流式对话。
3. 查看当前逻辑 State、native State 状态、revision、token 数和恢复方式。
4. 重置、新建、保存、加载会话。
5. 退出进程后，仅凭保存的 transcript 重建 State 并继续对话。
6. 生成期间第一次 `Ctrl-C` 只取消当前生成；空闲时 `Ctrl-C` 退出。
7. 取消、回调失败或 native 错误后不提交残缺消息，也不继续使用未知 State。
8. 模型、tokenizer、模板或 Initial State 不兼容时拒绝错误快照，并安全回退或报错。

第一阶段以 logical State 持久化和 transcript replay 为正确性基线。MLX native State 快照是同一方案中的性能增强项，但不能成为恢复会话的唯一条件。

## 2. 本次代码审查结论

### 2.1 仓库和构建基线

- `third_party/rwkv-mobile` 与 2026-07-28 上游 `master` 都位于提交 `a9a66e8`，当前没有 revision 漂移。
- 上游仓库另行克隆到 `/tmp/rwkv-mobile-analysis.HYGIrd/rwkv-mobile` 完成审查。
- 当前机器为 Apple Silicon；`go test ./...` 通过。
- `./scripts/build-mlx.sh` 可以生成 `dist/rwkv-cli`、`dist/librwkv_mobile.dylib`、Metal resource bundle 和 tokenizer。
- 没有配置 `RWKV_TEST_MODEL` 与 `RWKV_TEST_TOKENIZER`，因此本次只确认了构建和普通测试，没有完成真实模型行为验收。

### 2.2 RWKV Mobile 可复用的能力

| 能力 | 当前实现位置 | 结论 |
|---|---|---|
| MLX 模型加载与执行 | `src/backends/mlx/mlx_rwkv_backend.*` | 可复用 |
| tokenizer | `src/tokenizer.*` | 可复用 |
| sampler | `src/sampler.*` | 可复用 |
| token prefill/decode | `src/runtime.cpp`、MLX FFI | 可复用，但需要窄接口 |
| 内存 State get/set/zero | MLX backend | 可复用 |
| State Tree 前缀匹配 | `src/backend.*` | 可复用，但不能作为上层事实源 |
| MLX native State 导出 | 未实现 `serialize_runtime_state` | 需要补齐或先 replay |
| 同步 generation | `rwkvmobile_runtime_gen_completion` | 可短期复用，但语义不足 |

### 2.3 必须先修正的原生问题

1. `src/c_api.cpp` 的异步加载和生成使用 detached thread，并捕获裸 `Runtime *`。Runtime 销毁不能可靠等待这些任务。
2. generation callback 没有 `user_data` 和 `request_id`。当前 Go bridge 只能使用进程级全局 writer 和 generation mutex。
3. `ModelInstance::is_generating` 和 `stop_signal` 是普通 `bool`，读写没有完整同步。
4. `execution_provider` 的部分 State 默认实现返回成功。未实现的 capability 可能被误判为可用。
5. MLX backend 能把 cache 读入 `std::vector<__fp16>`，也能写回，但没有实现序列化和反序列化。
6. `Runtime::gen_completion` 只为输入 prompt 注册 checkpoint；生成完成后没有把完整输出 token 注册为 State checkpoint。下一轮无法证明 native State 与已提交 transcript 一致。
7. `Runtime::chat` 会注册输出 checkpoint，但其模板、停止规则和 State 事务全部封装在大 Runtime 中，不适合作为 Agent 的稳定边界。
8. `Runtime::clear_state` 只把当前 provider cache 清零，没有清除 State Tree。严格的 `/reset` 需要同时丢弃旧 checkpoint，防止后续前缀匹配重新载入旧 State。
9. 历史 State 文件是未版本化的 `[state][ids][logits]` 拼接，没有模型、tokenizer、模板、codec 指纹和 checksum。
10. 当前构建没有固定 macOS deployment target。在本机 beta SDK 下生成的二进制 `minos` 为 27.0，不能作为可分发产物。

### 2.4 RWKV-Agent 当前缺口

1. `cmd/rwkv-cli/main.go` 每轮只提交最新 user 消息，没有持有 transcript。
2. `signal.NotifyContext` 使用一个进程级 context；第一次 `Ctrl-C` 会永久取消整个 REPL。
3. `internal/native/mlx` 使用全局 callback 状态，无法自然支持多个请求。
4. `internal/inference/backend/mlx` 的 revision 只是递增整数，没有绑定 transcript 或模型语义。
5. 失败后直接调用 `ClearState`，没有 replay 已提交历史，且结束逻辑会把状态重新标记为 `clean`。
6. `ExportState`、`ImportState` 和 `Fork` 都是 `unsupported`。
7. prompt compiler 只有临时字符串模板，没有模板版本、token fingerprint 和 committed-prefix 不变量。

因此，正确的最短路径不是直接给当前 REPL 添加 `/save`，而是先完成一个安全、窄且可测试的 RWKV Agent Runtime，再在其上实现 Conversation 事务。

## 3. 范围与明确非目标

### 3.1 P0 范围

- macOS 15+、Apple Silicon。
- 单进程、单前台 Session。
- 单模型实例、单并发 generation。
- RWKV MLX safetensors 模型目录。
- text chat、stream、cancel、token count、reset、prefill/replay。
- logical session bundle。
- MLX native snapshot 能力查询；支持时使用，不支持时 replay。

### 3.2 P0 非目标

- Intel Mac。
- Windows、Linux 的高性能 provider。
- 多 Session 并行推理。
- HTTP server、TTS、vision、embedding、rerank。
- tool execution、RAG、长期记忆。
- 修改或编辑历史消息。
- 在不同模型、tokenizer、模板之间迁移 native State。

如果必须支持 Intel Mac，应单独增加 llama.cpp 或 NCNN provider；不能把 MLX 路径描述为“所有 macOS”。

## 4. 目标架构

```text
cmd/rwkv-cli
      │
internal/cli/repl
      │
internal/conversation
  transcript · turn transaction · revision · store
      │
internal/inference
  prompt compiler · Model · Session · capabilities
      │
internal/inference/backend/rwkvmobile
      │
internal/native/rwkvmobile
  cgo.Handle · error mapping · lifecycle
      │
librwkv_agent_runtime.dylib
  narrow versioned C ABI
      │
internal fork of RWKV Mobile
      │
MLXModelFFI · Metal
```

依赖规则：

- CLI 不直接调用 native 包。
- Conversation 不依赖 MLX 类型。
- Go backend 不依赖 RWKV Mobile 原始大 C API。
- `rwkv_agent_runtime` 不暴露 `Runtime *`、`std::any`、State Tree 节点或 provider 专有结构体。
- transcript 是事实源；native State 只是可校验、可丢弃的加速产物。

## 5. RWKV Mobile 采用和维护方式

### 5.1 建立内部 fork

在真正修改 native 代码前：

1. 创建 RWKV-Agent 所有的 RWKV Mobile fork。
2. 保留 `upstream` 指向 `MollySophia/rwkv-mobile`。
3. 将本仓库 submodule URL 改为内部 fork。
4. 从 `a9a66e8` 建立 `rwkv-agent-runtime-v1` 分支。
5. 每次升级只通过明确 PR 修改 submodule commit。

不采用在构建脚本中下载上游 HEAD，也不在主仓库维护一组难以审查的临时 patch。

### 5.2 新增独立构建产物

在 fork 中新增：

```text
src/agent_runtime/
├── rwkv_agent_runtime.h
├── rwkv_agent_runtime.cpp
├── runtime_impl.hpp
└── state_codec.cpp
```

CMake 新增 `rwkv_agent_runtime` target，链接 `rwkv_mobile_internal`。macOS CLI 只分发：

```text
dist/
├── rwkv-cli
├── librwkv_agent_runtime.dylib
├── mlx-swift_Cmlx.bundle/Contents/Resources/default.metallib
└── assets/rwkv_vocab_v20230424.txt
```

原始 `librwkv_mobile.dylib` 不再是 Go 层的直接 ABI 依赖。

## 6. `rwkv_agent_runtime` ABI v1

### 6.1 设计约束

- C ABI version 固定为 1；所有可扩展结构带 `struct_size`。
- runtime、model、session 都是 opaque handle。
- 加载、prefill、generate 都提供同步函数。
- Go 负责决定是否在 goroutine 中执行，不调用 detached async API。
- streaming callback 带 `request_id` 和 `user_data`，返回非零即请求取消。
- cancel 必须可从另一线程调用。
- destroy 必须先阻止新任务，再 cancel 并等待活动调用退出。
- 可选功能通过 capability bit 查询。
- 错误使用稳定 code；诊断文本通过 handle 的 last-error 读取。
- callback 中的字符串和 event 指针只在 callback 返回前有效。

### 6.2 最小接口

函数名可以在实现阶段微调，但语义必须保持：

```c
uint32_t rwa_abi_version(void);

rwa_status rwa_runtime_create(
    const rwa_runtime_options *options,
    rwa_runtime **out_runtime);
rwa_status rwa_runtime_destroy(rwa_runtime *runtime);

rwa_status rwa_model_load(
    rwa_runtime *runtime,
    const rwa_model_options *options,
    rwa_model **out_model);
rwa_status rwa_model_destroy(rwa_model *model);
rwa_status rwa_model_capabilities(
    const rwa_model *model,
    rwa_capabilities *out_capabilities);

rwa_status rwa_model_encode(
    rwa_model *model,
    const char *utf8,
    size_t utf8_size,
    rwa_token_buffer *out_tokens);
void rwa_token_buffer_free(rwa_token_buffer *buffer);

rwa_status rwa_session_create(
    rwa_model *model,
    const rwa_session_options *options,
    rwa_session **out_session);
rwa_status rwa_session_destroy(rwa_session *session);

rwa_status rwa_session_reset(
    rwa_session *session,
    rwa_reset_mode mode);

rwa_status rwa_session_sync_prefix(
    rwa_session *session,
    const int32_t *token_ids,
    size_t token_count,
    rwa_prefill_progress_callback callback,
    void *user_data);

rwa_status rwa_session_generate(
    rwa_session *session,
    const rwa_generate_options *options,
    rwa_stream_callback callback,
    void *user_data,
    rwa_generate_result *out_result);

rwa_status rwa_session_cancel(
    rwa_session *session,
    uint64_t request_id);

rwa_status rwa_session_export_state(
    rwa_session *session,
    rwa_writer writer,
    void *user_data,
    rwa_state_descriptor *out_descriptor);

rwa_status rwa_session_import_state(
    rwa_session *session,
    rwa_reader reader,
    void *user_data,
    const rwa_state_descriptor *descriptor);
```

`rwa_generate_options` 接收精确 token IDs：

```c
typedef struct {
    uint32_t struct_size;
    uint64_t request_id;
    const int32_t *input_token_ids;
    size_t input_token_count;
    uint32_t max_output_tokens;
    float temperature;
    int32_t top_k;
    float top_p;
    float presence_penalty;
    float frequency_penalty;
    float penalty_decay;
    uint64_t seed;
    uint32_t has_seed;
} rwa_generate_options;
```

stream event 至少区分 token delta、finish 和 warning，并携带 token ID。最终 result 返回：

- 实际输出 token IDs；
- 完整 UTF-8 输出；
- `stop`、`length`、`cancelled` 或 `error`；
- prefill/decode token 数；
- prefill/decode 速度；
- native prefix hash；
- State 是否仍为 clean。

### 6.3 并发和生命周期实现

`rwa_session` 内部维护：

- `operation_mutex`：串行 prefill、generate、reset、import/export。
- `cancel_requested`：原子变量。
- `active_request_id`：原子变量。
- `lifecycle_mutex + condition_variable`：destroy 等待活动调用。
- `status`：`clean/generating/dirty/closed`。
- `committed_prefix_tokens` 与 `committed_prefix_hash`。

cancel 不获取会被 generation 长时间持有的 operation mutex，只设置与 request ID 匹配的原子取消标志。

### 6.4 对 RWKV Mobile 内部的具体修正

1. 将 `stop_signal` 改为受同步保护的状态，不再裸读写普通 `bool`。
2. 增加 token-ID 版本的 prefill 和 generation，避免字符串边界重新 tokenize。
3. generation 正常结束时，为“输入 prefix + 实际已 eval 的输出 token”注册 checkpoint。
4. callback 返回取消、用户取消或 native 错误时，将 Session 标为 `dirty`，不能报告成功。
5. hard reset 同时执行 provider zero、清空 State Tree、重新建立 root checkpoint。
6. provider 未实现的 State 操作默认返回 `RWKV_ERROR_UNSUPPORTED`。
7. MLX codec 只接受预期长度的 fp16 cache；禁止尺寸不匹配的导入。
8. 所有读取 state 文件的长度字段先做上限、溢出和剩余文件长度校验。

## 7. Prompt 与 prefix 一致性

### 7.1 单一模板实现

增加版本化模板：

```text
template_id: rwkv-g1-chat
template_version: 1
```

Go 的 prompt compiler 是 CLI 使用的唯一模板实现。它必须覆盖：

- role 名称；
- BOS/EOS；
- role 后空格；
- reasoning 开关和 thinking marker；
- assistant generation prompt；
- flower template 标志；
- 换行归一化规则。

模型加载时生成 `PromptProfile`，不允许 CLI 拼接 `"User:"` 或 `"<think>"`。

### 7.2 `CompiledTurn`

```go
type CompiledTurn struct {
    InputText       string
    InputTokens     []TokenID
    InputHash       string
    TemplateID      string
    TemplateVersion int
}
```

每次请求传入“完整已提交消息 + 候选 user 消息”。生成成功后，backend 把 assistant 输出追加到候选消息，再编译 committed transcript。

必须保持以下不变量：

```text
native_prefix_tokens == compile(committed_transcript).tokens
```

生成后的同步规则：

1. 如果 native 实际 token 是 committed tokens 的前缀，只 prefill 缺少的提交后缀。
2. 如果两者完全一致，直接提交。
3. 如果 token 边界、stop token 或模板导致不匹配，hard reset 后 prefill 完整 committed tokens。
4. 只有完成上述同步，`GenerateResult.Committed` 才能为 `true`。

这解决 assistant 输出重新编码、停止符处理和下一轮 prefix 漂移问题。

## 8. Conversation Turn 事务

增加：

```text
internal/conversation/
├── conversation.go
├── turn.go
├── revision.go
├── restore.go
├── state.go
└── store/
    ├── manifest.go
    ├── jsonl.go
    └── atomic.go
```

一次普通输入的事务顺序：

1. 检查 Session 是否 `clean`；若为 `dirty`，先从已提交 transcript rebuild。
2. 创建候选 user 消息，不修改已提交 transcript。
3. 编译完整候选历史并调用 `Session.Generate`。
4. delta 只输出到终端并暂存在 turn buffer。
5. generation 正常完成后，把 assistant 完整输出加入候选 transcript。
6. backend 将 native prefix 同步到编译后的 committed transcript。
7. 计算 transcript hash 和新 revision。
8. 在内存中原子替换已提交 transcript、revision 和 State 元数据。
9. 如果启用 autosave，再写不可变 session revision。

失败或取消：

- user 和残缺 assistant 都不进入 transcript；
- logical revision 不变；
- native Session 标为 `dirty`；
- 下一轮、`/save` native snapshot 或 `/state --verify` 前执行 replay；
- `/save` 可以保存上一个 clean logical revision，但不能把 dirty native State 写入 `state.bin`。

`/load` 使用两阶段替换：

1. 创建临时 Conversation 和 native Session。
2. 完成 manifest 校验、native import 或 replay。
3. 全部成功后才替换当前会话。
4. 失败时原会话保持可用。

## 9. Revision、指纹和 State 状态

### 9.1 Canonical revision

使用确定性的 canonical JSON 编码消息，revision 为：

```text
SHA-256(
    schema_version
    + parent_revision
    + canonical_committed_turn
    + model_fingerprint
    + tokenizer_fingerprint
    + template_id_and_version
    + initial_state_fingerprint
)
```

revision 使用完整 `sha256:<hex>` 持久化；CLI 默认显示前 12 个十六进制字符。

### 9.2 必须持久化的兼容性信息

- 模型文件内容指纹和模型格式。
- tokenizer 内容指纹。
- prompt template ID、版本和 profile hash。
- Initial State 指纹；没有时记录空值。
- RWKV Agent Runtime ABI version。
- RWKV Mobile commit，仅用于诊断。
- native codec ID 和 codec version。
- transcript hash。
- native state checksum。

### 9.3 状态定义

| 状态 | 含义 | 允许操作 |
|---|---|---|
| `clean` | native prefix 与 logical revision 一致 | generate/save/export/reset |
| `generating` | 正在修改候选 State | cancel/state |
| `dirty` | native 位置未知 | rebuild/reset/保存 logical State |
| `rebuilding` | 从 transcript prefill | cancel/state |
| `closed` | 已释放 | 无 |

## 10. Session bundle v1

为避免替换非空目录时出现跨平台非原子行为，使用不可变 revision 目录和一个原子更新的 `CURRENT` 指针：

```text
demo.rwkv-session/
├── CURRENT
└── revisions/
    └── sha256-abc123.../
        ├── session.json
        ├── transcript.jsonl
        └── state.bin          # 可选
```

保存：

1. 在 `revisions/` 下创建同文件系统的临时目录。
2. 写 transcript、可选 native State 和 manifest。
3. 逐个 flush/fsync，计算并复核 hash。
4. rename 临时目录为不可变 revision 目录。
5. 写 `CURRENT.tmp`，fsync 后 rename 为 `CURRENT`。
6. fsync bundle 根目录。
7. 默认保留最近两个 revision，垃圾回收不影响当前保存成功。

加载：

1. 读取 `CURRENT`，拒绝路径穿越和符号链接逃逸。
2. 解析有大小上限的 manifest 和 JSONL。
3. 校验 schema、hash、消息 role 和 UTF-8。
4. 校验模型、tokenizer、模板和 Initial State。
5. native State 存在且 codec 完全兼容时尝试导入。
6. 导入失败时丢弃 native State，并从 transcript replay；不得带着部分导入的 State 继续。
7. replay 后核对 token count、prefix hash 和 revision。

`state.bin` v1 使用明确 magic、version、整数端序、长度和 codec ID；外层 manifest 再保存 SHA-256。它至少包含 recurrent cache、精确 prefix token IDs 和下一 token logits。

## 11. Go 接口和包调整

### 11.1 inference 类型

在 `internal/inference/types.go` 增加：

```go
type PrefillRequest struct {
    Tokens        []TokenID
    ReplacePrefix bool
}

type PrefillResult struct {
    TokenCount   int
    PrefixHash   string
    StateRevision string
}
```

`Session` 增加 `Prefill`。`SessionStateInfo` 增加：

- logical/native revision；
- status；
- committed prefix token 数；
- native snapshot capability；
- recovery mode；
- dirty reason。

### 11.2 backend 和 native adapter 改名

目标目录：

```text
internal/inference/backend/rwkvmobile/
├── backend.go
├── model.go
├── session.go
├── capability.go
└── contract_integration_test.go

internal/native/rwkvmobile/
├── runtime.go
├── runtime_darwin_arm64.go
├── runtime_stub.go
├── bridge.h
└── callback.go
```

`mlx` 成为 provider 配置：

```go
rwkvmobile.New(rwkvmobile.Options{Provider: "mlx"})
```

callback context 使用 `runtime/cgo.Handle`：

1. 调用前创建 handle。
2. 把整数 handle 转成 `uintptr_t user_data`。
3. callback 只在同步 native 调用期间使用。
4. native 返回后删除 handle。
5. native 绝不跨调用保存 Go handle 或 Go 指针。

### 11.3 错误映射

Native code 固定映射到：

- `ErrInvalidArgument`
- `ErrUnavailable`
- `ErrUnsupported`
- `ErrBusy`
- `ErrCancelled`
- `ErrIncompatibleState`
- `ErrCorruptState`
- `ErrBackendFailure`
- `ErrClosed`

错误 message 保留 native 上下文，但上层逻辑不能解析 message 判断类型。

## 12. CLI 设计

### 12.1 参数

```text
rwkv-cli run
  --model <dir>                 必填
  --backend auto|rwkvmobile
  --provider auto|mlx
  --tokenizer <file>            默认模型目录，其次 dist/assets
  --session <bundle>
  --prompt <text>               可选，单轮模式
  --max-tokens <n>
  --temperature <f>
  --top-k <n>
  --top-p <f>
  --reasoning
  --autosave
  --native-state auto|off|required
```

### 12.2 REPL 命令

| 命令 | 实现语义 |
|---|---|
| 普通文本 | 候选 turn，成功后提交 |
| `/state` | 展示 revision、状态、token、provider、恢复方式、dirty reason |
| `/history` | 输出已提交 transcript |
| `/save [path]` | 保存 clean logical revision；native State 可选 |
| `/load <path>` | 两阶段校验并替换 |
| `/reset` | 清 transcript，hard reset native State |
| `/new` | `/reset` 的别名 |
| `/help` | 展示命令 |
| `/exit` | cancel/wait/可选 autosave/逆序 close |

### 12.3 Signal 处理

不能继续使用单一的 `signal.NotifyContext`：

- REPL 维护进程生命周期 context。
- 每个 turn 创建独立 generation context。
- signal goroutine 根据当前状态分派：
  - `generating/rebuilding`：第一次 `Ctrl-C` 调用本轮 cancel。
  - `idle`：请求退出。
  - 取消尚未完成时第二次 `Ctrl-C`：再次提示并允许强制退出，但先尽最大努力等待 native 同步调用返回。
- SIGTERM 执行 cancel、有限等待和关闭。

## 13. macOS 构建与分发

将 `scripts/build-mlx.sh` 收敛为 `scripts/build-macos.sh`，至少完成：

1. 校验 `Darwin/arm64`、CMake、Ninja、Go、Xcode/Swift。
2. 固定：

```text
CMAKE_OSX_ARCHITECTURES=arm64
CMAKE_OSX_DEPLOYMENT_TARGET=15.0
MACOSX_DEPLOYMENT_TARGET=15.0
```

3. 只启用 MLX，禁用 server、TTS、vision、whisper 和其他 provider。
4. 构建 `librwkv_agent_runtime.dylib`。
5. 设置 dylib install name 为 `@rpath/librwkv_agent_runtime.dylib`。
6. 给 CLI 增加 `@executable_path` rpath。
7. 复制 metallib bundle 和 tokenizer。
8. 用 `otool -L`、`vtool -show-build` 和一次无模型 `--help` smoke test 验证产物。
9. 生成包含 commit、ABI、Go version、deployment target 和 SHA-256 的 build manifest。

发布版本再增加 codesign、hardened runtime 和 notarization。开发版先保证解压后在另一台满足最低系统版本的 Apple Silicon Mac 可运行。

## 14. 实施里程碑和 PR 顺序

### PR 0：冻结基线与可重复构建（1–2 人日）

- 建立内部 fork 和 submodule pin。
- 固定 deployment target。
- 增加 build manifest 与 `otool/vtool` 检查。
- 保存一组小型真实模型验收配置，但不提交模型权重。

验收：

- 普通 Go tests 通过。
- macOS native build 可重复。
- 二进制不再错误要求 macOS 27。

### PR 1：Native ABI 与生命周期（3–5 人日）

- 新增 `rwkv_agent_runtime` target、opaque handles、ABI version 和错误码。
- 同步 load/generate、带 `user_data` 的 callback。
- thread-safe cancel 和 destroy/wait。
- capability 查询。
- hard reset。

验收：

- callback 不使用进程级全局 writer。
- generate/cancel/close 并发测试无悬空线程。
- ASan native lifecycle tests 通过。

### PR 2：精确 token prefix 与 checkpoint（3–5 人日）

- token encode API。
- token-ID prefill/generate。
- 输出 token checkpoint。
- dirty 状态和 prefix hash。
- prompt/template golden tests。

验收：

- full prefix、suffix prefill 和 mismatch rebuild 三条路径可测。
- 取消后拒绝继续 append，必须 rebuild。
- 流式输出拼接等于最终输出。

### PR 3：Go rwkvmobile adapter（2–3 人日）

- 新建 `internal/native/rwkvmobile`。
- 使用 `cgo.Handle` 路由 callback。
- 新建 `backend/rwkvmobile` 并迁移 MLX adapter。
- 补齐 `Prefill`、capability 和错误映射。

验收：

- 删除 generation 全局 mutex 和全局 writer。
- `go test -race ./...` 通过。
- mock 与 native contract tests 对相同语义通过。

### PR 4：Conversation 和事务（3–5 人日）

- 结构化 transcript。
- 候选 turn、成功提交和失败回滚。
- canonical revision。
- dirty rebuild。
- `/history` 和 `/state` 所需查询。

验收：

- 五轮上下文测试。
- cancel、sink error、native error 均不污染 transcript。
- replay 后 prefix hash 与 logical revision 一致。

### PR 5：Session store 与命令（4–6 人日）

- immutable revision bundle 和 `CURRENT`。
- `/save`、`/load`、`/reset`、`/new`。
- 模型、tokenizer、模板和 checksum 校验。
- logical-only replay。
- 两阶段 load。

验收：

- 删除 `state.bin` 后可恢复。
- 损坏 transcript 被拒绝。
- 不兼容模型被拒绝。
- 模拟保存中断后仍能读取上一个 revision。

### PR 6：Ctrl-C、CLI 收尾和打包（2–4 人日）

- per-turn cancel。
- 加载和 rebuild 进度。
- 结构化诊断。
- 分发目录 smoke test。
- 用户 README。

验收：

- 生成期间一次 `Ctrl-C` 回到 prompt。
- 空闲 `Ctrl-C` 正常退出。
- 退出顺序为 turn → session → model → runtime。

### PR 7：MLX native snapshot（可与 PR 6 并行，2–4 人日）

- MLX fp16 State codec。
- prefix tokens 和 logits 一并导出。
- `state.bin` checksum 和 codec capability。
- native import 失败自动回退 replay。

验收：

- native snapshot 恢复与 replay 的下一 token logits 在允许误差内一致。
- 截断、篡改、错误尺寸和错误模型的快照全部被拒绝。

### PR 8：macOS 多 Session 并发与 Continuous Batch（5–8 人日）

- 在 Model 层增加单一 scheduler worker，禁止多个业务线程直接并发调用同一个 MLX model。
- 将 macOS MLX 最多 16 个 batch State slot 建模为可租用资源，每个活跃 Session 独占一个 slot。
- prefill 按 Session 分块调度，decode 将多个活跃 Session 的单 token 请求动态合并为 continuous batch。
- 为每个请求维护独立的 `request_id`、callback、sampler、stop 条件、token buffer 和取消状态。
- 一个请求取消、结束或失败时只回收自己的 slot，不修改其他 Session 的 State。
- slot 用尽时进入有界 FIFO 队列并提供 backpressure；不得临时重复加载模型。
- State export/import、dirty rebuild 和 session close 都按 slot 执行，空闲 Session 可以导出 State 后释放 slot。
- capability 明确报告 `max_state_slots`、当前可用 slot、最大 active batch 和队列上限。
- CLI 首版仍是单前台会话；并发能力通过 contract test 和后续 server/Agent Harness API 暴露。

验收：

- 一个模型只加载一次，至少 8 个 Session 能重叠生成，并且 native instrumentation 证明 decode batch size 曾大于 1。
- 8 路流式输出、token、revision 和 State 完全隔离，没有 callback 串线。
- 取消其中一个请求不会停止、污染或重置其他请求。
- 第 17 个活跃请求按策略排队或返回明确的 capacity 错误，不崩溃、不泄漏 slot。
- batch size 1 的输出语义和 PR 7 前保持一致。
- `go test -race`、native ASan、连续创建/关闭 Session 和 scheduler shutdown tests 通过。
- 输出 batch 1/2/4/8/16 的吞吐、首 token 延迟和内存报告，性能门禁以同一模型、同一生成参数的串行基线为参照。

P0 可在 PR 6 完成后交付，PR 7 是 State 恢复性能增强，PR 8 是单进程共享模型并发增强。P0 单人串行预计 18–30 人日；完成 PR 0–8 的完整路线预计 25–42 人日。如果 native ABI、Conversation/store 和 scheduler 分开开发，可压缩日历时间，但合并仍必须按依赖顺序验收。

## 15. 测试矩阵

### 15.1 不依赖真实模型

- prompt/template golden tests。
- transcript canonical encoding 和 revision tests。
- candidate turn 成功/取消/错误事务测试。
- dirty → rebuilding → clean 状态机测试。
- bundle 原子保存、损坏、大小上限和路径安全测试。
- mock backend prefix match/mismatch tests。
- callback `user_data` 隔离、cancel race 和 close race。
- unsupported capability 不得返回成功。
- scheduler slot 租用、排队、公平性、独立取消和 shutdown tests。

### 15.2 真实模型测试

使用固定模型、tokenizer 和确定性 seed：

1. 加载并生成非空输出。
2. 五轮记忆测试。
3. 第三轮取消，第四轮上下文仍只包含前两轮。
4. 保存、退出、加载、继续提问。
5. 删除 `state.bin` 后 replay。
6. 导入 native State 后继续生成。
7. 修改 tokenizer、模板、模型各触发一次不兼容错误。
8. 截断 transcript 和 state 各触发一次 checksum 错误。
9. 连续执行 50 次 generate/reset，检查泄漏和崩溃。
10. 同一模型执行 batch 1/2/4/8/16，多 Session 输出和 State 不串线。

### 15.3 工具和门禁

```sh
go test ./...
go test -race ./...
./scripts/build-macos.sh
./scripts/test-macos-native.sh
./scripts/test-macos-real-model.sh
```

Native 层增加 ASan job。真实大模型测试可以是手动或 nightly，但每次 RWKV Mobile submodule 升级必须运行。

## 16. 风险与控制

| 风险 | 影响 | 控制 |
|---|---|---|
| 模板与生成后 token 不一致 | State 漂移 | committed prefix 重编译、比较、必要时完整 replay |
| cancel 已经修改 provider State | 下一轮污染 | 标记 dirty，禁止 append，rebuild |
| native snapshot 格式变化 | 崩溃或错误上下文 | codec version、尺寸校验、checksum、replay fallback |
| State Tree 在 reset 后泄漏历史 | `/reset` 不彻底 | hard reset 清 provider 和整棵 tree |
| callback 生命周期错误 | 崩溃/UAF | 同步 callback、`cgo.Handle`、destroy wait |
| 模型 fingerprint 计算慢 | 启动慢 | converter 生成 manifest；缓存只能作为优化，首次仍校验 |
| beta SDK 污染 deployment target | 产物无法分发 | 固定 target 并用 `vtool` 门禁 |
| 上游升级破坏 facade | 隐性回归 | 固定 commit、contract tests、显式升级 PR |
| native State 体积大 | 保存慢、占磁盘 | 可选快照、流式写、保留最近 revision、logical-only 模式 |
| 多线程直接调用同一 MLX model | State 串线、GPU 争用或崩溃 | 单 scheduler worker、slot 所有权和 continuous batch |

## 17. P0 完成定义

以下条件全部满足才可标记完成：

1. Apple Silicon macOS 15+ 上，一个构建命令生成可运行的分发目录。
2. 一个 CLI 命令加载模型并进入 REPL。
3. 五轮对话使用完整 transcript，能引用早先信息。
4. 每轮只在 native prefix 与 committed transcript 对齐后提交。
5. `/state`、`/history`、`/save`、`/load`、`/reset`、`/new`、`/exit` 可用。
6. 不支持或删除 native snapshot 时，可通过 transcript replay 恢复。
7. generation cancel 和 sink error 不提交残缺 turn。
8. dirty State 在下一轮前重建，不会被误报为 clean。
9. 不兼容或损坏的 bundle 被明确拒绝。
10. Runtime、Model、Session 的关闭顺序有自动化生命周期测试。
11. `go test ./...`、`go test -race ./...`、native ASan 和至少一组固定真实模型验收通过。
12. 分发二进制的 deployment target、rpath、dylib 和 Metal resource 均通过自动检查。

## 18. 建议立即开始的工作

第一批只做 PR 0 和 PR 1，不同时铺开 CLI 命令：

1. 建内部 fork并固定 submodule。
2. 增加 `librwkv_agent_runtime.dylib` 最小 target。
3. 先实现 ABI/version/error/capability/create/load/generate/cancel/destroy。
4. 用假 callback 和短 real-model generation 证明生命周期。
5. 删除 Go 的全局 callback writer 后，再进入 Conversation 和 State store。

这个顺序先消除最底层的不确定生命周期和 callback 约束，后续 transcript、State revision 和 CLI 命令才有稳定承载面。
