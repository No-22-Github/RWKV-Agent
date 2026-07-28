# RWKV Mobile 采用方案与 CLI 多轮对话里程碑

状态：Implementation Draft v0.1

适用范围：RWKV-Agent 的第一个可持续使用版本

短期目标：从终端启动本地模型，完成可靠的多轮对话，并能够检查、重置、保存和恢复会话 State

关联文档：[跨平台推理核心设计](inference-core-design.md)

## 1. 决策

RWKV-Agent 采用以下路线：

1. **使用内部固定版本的 RWKV Mobile 作为底层推理引擎。**
2. **不从零重写各个平台的模型执行后端。**
3. **不让 Agent、CLI 或 Go 推理接口直接依赖 RWKV Mobile 当前的完整 C API。**
4. **在 RWKV Mobile 之上维护一个窄的、版本化的 `rwkv_agent_runtime` 边界。**
5. **会话、transcript、State revision、恢复策略和并发调度由 RWKV-Agent 管理。**
6. **短期只完成当前 MLX 路径，不在这个里程碑中增加新的推理后端。**

审查基线为 2026-07-28，本仓库 submodule 固定在 RWKV Mobile `a9a66e8bea2a708d6ca14ccb9bb46c721a5b7fdd`；当时它与上游 `master` HEAD 一致。后续升级必须显式修改 revision 并运行完整 contract/integration tests，不能在构建时自动追踪上游 HEAD。

这里的“采用”不是把 RWKV Mobile 当作不可修改的外部黑盒，而是把它当作内部推理基础设施：

- 保留并复用 execution provider、模型加载、tokenizer、采样、prefill、decode 和底层 State 操作。
- 根据 Agent 的需要修正生命周期、回调、Capability 和 State 接口。
- 上层只依赖 RWKV-Agent 自己定义的稳定语义。

目标架构如下：

```text
rwkv-cli
   │
Conversation / Transcript Store
   │
inference Core → Model → Session
   │
rwkvmobile backend adapter
   │
rwkv_agent_runtime C ABI
   │
internal fork of RWKV Mobile
   │
MLX / future desktop providers
```

## 2. 为什么不直接使用原始 C API

RWKV Mobile 已经解决了多平台推理中成本最高的部分，但它现有的公共接口还不适合作为 Agent 的长期边界。

当前需要在我们的边界内解决的问题包括：

- 部分异步接口创建 detached thread，并捕获裸 Runtime 指针；Runtime 释放不会等待这些任务结束。
- generation callback 没有 `user_data`，跨语言绑定只能依赖进程级全局状态。
- `is_generating`、`stop_signal` 和模型容器没有完整的并发保护。
- Runtime 中没有独立的一等 Session handle；一个模型实例主要对应一份当前可变 State。
- 不同 provider 的 State get/set、序列化、batch 等能力并不一致。
- 历史 State 文件没有外层格式版本、模型指纹、tokenizer/template 指纹和 checksum。
- 当前 CI 主要验证构建和打包，没有统一的后端行为契约测试。

因此，短期可以继续复用同步生成和底层 State 能力，但不能把这些限制泄漏给 CLI 和未来的 Agent Harness。

## 3. 短期产品目标

### 3.1 用户路径

保留现有命令入口：

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/model \
  --backend auto
```

没有传入 `--prompt` 时进入交互模式：

```text
Loading model...
Session: new
Backend: mlx

> 我叫小明，请记住。
assistant> 好的，我记住了。

> 我叫什么？
assistant> 你叫小明。

> /state
revision: 2
status: clean
messages: 4
tokens: 37
native_snapshot: unavailable

> /save ./sessions/demo
saved: ./sessions/demo

> /exit
```

恢复会话：

```sh
./dist/rwkv-cli run \
  --model /absolute/path/to/model \
  --session ./sessions/demo
```

### 3.2 第一版 REPL 命令

| 命令 | 行为 |
|---|---|
| 普通文本 | 追加一条 user 消息并流式生成 assistant 消息 |
| `/state` | 显示 revision、状态、消息数、token 数和恢复方式 |
| `/history` | 输出当前 transcript，不包含 native 日志 |
| `/save [path]` | 原子保存会话；没有 path 时保存到启动时的 `--session` |
| `/load <path>` | 校验并载入另一个会话 |
| `/reset` | 清空 transcript，并将 recurrent State 恢复到 Initial State 或零 State |
| `/new` | `/reset` 的别名，开始新会话 |
| `/help` | 显示可用命令 |
| `/exit` | 安全停止生成、保存可选的自动存档并退出 |

第一版只允许一个前台交互 Session。多个 Session 的并发执行不属于这个里程碑，但会话文件格式和推理接口不能阻止后续扩展。

### 3.3 中断语义

- 生成期间第一次 `Ctrl-C` 只取消当前生成，REPL 继续运行。
- 没有生成任务时 `Ctrl-C` 退出程序。
- 取消后不得把不完整 assistant 消息提交到 transcript。
- 如果 provider 无法回滚到生成前 State，Session 标记为 `dirty`，下一次生成前从已提交 transcript 自动重建。

## 4. 当前基线与缺口

仓库当前已经具备：

- `Core → Model → Session` 的后端无关 Go 接口。
- deterministic mock backend 和 contract test 骨架。
- MLX adapter 和同步流式生成。
- 模型加载、token 计数、取消和 State reset。
- 单次 prompt 模式和逐行交互模式。
- 进程级 generation mutex，规避无 `user_data` callback 的串线问题。

当前交互模式还不是完整的多轮会话：

- CLI 没有持有并提交结构化 transcript。
- 每轮请求只包含当前 user 消息。
- Session revision 只是内存计数，没有绑定 transcript hash。
- 取消或 sink error 后会清空 native State，但没有从 transcript 重建。
- State export/import 尚未实现。
- 没有 session manifest、模型兼容性校验和 `/save`、`/load` 命令。
- native adapter 仍然以 `mlx` 命名，尚未形成通用 RWKV Mobile 边界。

所以接下来的工作重点不是再做一个生成 Demo，而是补齐“对话事实源、State 一致性和恢复闭环”。

## 5. 多轮对话的事实源

### 5.1 Transcript 是事实源

每个 Session 必须维护按顺序提交的结构化消息：

```go
type Conversation struct {
    ID       string
    Messages []inference.Message
    Revision string
}
```

一次成功 turn 的提交顺序是：

1. 接收 user 消息，但暂不修改已提交 transcript。
2. 将“完整已提交 transcript + 候选 user 消息”作为本次 `GenerateRequest.Messages`。
3. 流式文本只发送到终端，尚不成为历史。
4. 生成成功且 State 与完整输出一致时，原子提交 user 和 assistant 两条消息。
5. 计算新的 transcript hash，并将它作为 Session revision 的输入。
6. 保存或更新对应的 State 元数据。

失败或取消时：

- user 和不完整 assistant 都不进入已提交 transcript。
- 已提交 transcript revision 不变。
- native State 能回滚时恢复旧 State。
- 不能回滚时标记为 `dirty`，之后从 transcript 重建。

### 5.2 精确 Prompt 前缀

不能只保存“看起来一样”的文本。State 必须绑定生成它的精确输入语义：

- 消息 role 和顺序；
- Prompt template ID 与版本；
- reasoning 开关；
- BOS、EOS 和 role token；
- tokenizer 指纹；
- Initial State 指纹；
- 已提交 assistant 输出。

Prompt compiler 应当产生可哈希的 `CompiledTurn`：

```go
type CompiledTurn struct {
    Text            string
    TokenIDs        []inference.TokenID
    TemplateID      string
    TemplateVersion int
    PrefixHash      string
}
```

Conversation 每次都传完整候选历史，不负责判断 native State 当前走到哪里。Session 编译完整 token 前缀并与自己的 committed prefix 比较：

- committed prefix 完全匹配时，只 prefill 新增的精确 token 后缀；
- 历史被编辑、模板变化或 prefix 不匹配时，拒绝复用当前 State；
- 恢复或 State 失效时，清空 native State，然后按同一模板重新编译并 prefill 完整 transcript。

CLI 不能为了优化而只传最新一条 user 消息，否则 Session 无法验证 State 和逻辑历史是否仍然一致。

## 6. State 管理模型

### 6.1 两层 State

第一版明确区分两层 State：

| 层级 | 内容 | 是否必须持久化 | 用途 |
|---|---|---:|---|
| Logical State | transcript、revision、模型和模板指纹 | 是 | 正确性与跨 provider 恢复 |
| Native State | provider 的 recurrent State、token prefix、logits | 否 | 快速恢复与避免重复 prefill |

这意味着“管理 State”不等同于“必须马上让所有 provider 导出同一种二进制 State”。

即使当前 provider 不支持 native State export，下面的行为也必须成立：

- `/reset` 正确清零；
- `/state` 能报告状态与 revision；
- `/save` 能保存完整可恢复的会话；
- `/load` 能通过 transcript replay 重建；
- State 不兼容时能够明确拒绝快照并安全回退到 replay。

### 6.2 Session 状态机

```text
             generate
   clean ───────────────► generating
     ▲                         │
     │ success + commit        │ cancel / failure
     └─────────────────────────┤
                               ▼
                         clean or dirty
                               │
                               │ rebuild from transcript
                               ▼
                             clean
```

状态定义：

- `clean`：native State 与已提交 transcript revision 一致。
- `generating`：有一个正在修改候选 State 的请求。
- `dirty`：native State 的确切位置未知，不能继续追加生成。
- `rebuilding`：正在从 Initial/zero State 和 transcript 恢复。
- `closed`：Session 已释放。

任何会修改 State 的操作都必须在 Session 内串行执行。

### 6.3 Revision

Revision 不能只使用进程内递增整数。建议内容至少包含：

```text
revision = SHA-256(
    parent_revision
    + committed_message_bytes
    + model_fingerprint
    + tokenizer_fingerprint
    + template_id_and_version
    + initial_state_fingerprint
)
```

对外可以显示缩短后的 revision，但持久化文件保存完整值。

### 6.4 Session bundle

会话保存为目录，而不是单个不可检查的 blob：

```text
demo.rwkv-session/
├── session.json
├── transcript.jsonl
└── state.bin          # 可选
```

`session.json` 至少包含：

```json
{
  "schema_version": 1,
  "session_id": "01...",
  "revision": "sha256:...",
  "model_fingerprint": "sha256:...",
  "last_provider": "mlx",
  "tokenizer_fingerprint": "sha256:...",
  "prompt_template": {
    "id": "rwkv-g1-chat",
    "version": 1
  },
  "initial_state_fingerprint": "",
  "transcript_hash": "sha256:...",
  "native_state": {
    "present": false,
    "provider": "",
    "codec": "",
    "checksum": ""
  }
}
```

`last_provider` 只用于诊断，不限制 logical State 的 replay。只有可选的 native State 快照与其 `provider`、`codec` 绑定。

保存规则：

- 先写同目录临时 bundle；
- `fsync` 必要文件；
- 校验 transcript hash；
- 原子 rename 替换目标；
- 失败时保留旧 bundle。

加载规则：

1. 解析并校验 schema；
2. 校验 transcript hash；
3. 校验模型、tokenizer、模板和 Initial State 指纹；
4. 若 native State 存在且 codec capability 匹配，则导入并校验 revision；
5. 否则清空 native State，通过 transcript replay 重建；
6. 完成后才把 Session 暴露给 CLI。

不得静默使用不兼容 State，也不得只保存 `state.bin` 而丢失 transcript。

## 7. `rwkv_agent_runtime` 边界

### 7.1 原则

第一版 C ABI 只暴露 CLI 和统一推理核心真正需要的能力：

- 所有 handle 都是 opaque handle。
- ABI 有明确版本。
- 同步函数返回最终错误；异步由我们自己的受控 worker 实现。
- streaming callback 必须带 `request_id` 和 `user_data`。
- Runtime 销毁前必须取消并等待所有 worker。
- 每个可选能力都可以查询，不能靠调用失败来猜测。
- 错误由稳定 code 和可读取 message 组成。

### 7.2 建议的最小接口

以下是语义草案，不要求函数名逐字一致：

```c
uint32_t rwa_abi_version(void);

rwa_status rwa_runtime_create(
    const rwa_runtime_options *options,
    rwa_runtime **out_runtime);

rwa_status rwa_runtime_destroy(rwa_runtime *runtime);

rwa_status rwa_runtime_list_providers(
    rwa_runtime *runtime,
    rwa_provider_info *items,
    size_t *count);

rwa_status rwa_model_load(
    rwa_runtime *runtime,
    const rwa_model_options *options,
    rwa_model **out_model);

rwa_status rwa_model_destroy(rwa_model *model);

rwa_status rwa_session_create(
    rwa_model *model,
    const rwa_session_options *options,
    rwa_session **out_session);

rwa_status rwa_session_reset(rwa_session *session);
rwa_status rwa_session_destroy(rwa_session *session);

rwa_status rwa_session_prefill(
    rwa_session *session,
    const int32_t *token_ids,
    size_t token_count);

rwa_status rwa_session_generate(
    rwa_session *session,
    const rwa_generate_options *options,
    rwa_stream_callback callback,
    void *user_data);

rwa_status rwa_session_cancel(rwa_session *session);

rwa_status rwa_session_export_state(
    rwa_session *session,
    rwa_writer writer,
    void *user_data);

rwa_status rwa_session_import_state(
    rwa_session *session,
    rwa_reader reader,
    void *user_data);
```

stream callback：

```c
typedef int (*rwa_stream_callback)(
    uint64_t request_id,
    const rwa_stream_event *event,
    void *user_data);
```

`rwa_generate_options` 至少包含：

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
} rwa_generate_options;
```

generation 应接收精确 token IDs，不能把已计算好的 token 后缀重新当作字符串编码，否则 tokenizer 在拼接边界上的差异可能使 State prefix 漂移。所有可扩展 ABI 结构都带 `struct_size`，以支持向后兼容地增加字段。

Go bridge 使用 `runtime/cgo.Handle` 或等价的整数句柄传递 callback context；不得把普通 Go 指针作为长期 `user_data` 保存到 C。

如果底层 provider 暂时只能维护一份当前 State，facade 第一版可以声明：

```text
max_sessions_per_model = 1
max_concurrent_generations = 1
```

这是一项显式 Capability，不应通过偶发的 `busy` 或数据竞争表现出来。

### 7.3 第一版不暴露的接口

以下 RWKV Mobile 功能不进入短期 ABI：

- HTTP Server；
- TTS、vision、embedding、rerank；
- batch generation；
- backend 专有结构体直接透传；
- State Tree 节点或 `std::any`；
- 裸内部日志缓冲区；
- detached async API。

保留这些底层实现不等于必须把它们变成 Agent 的公共能力。

## 8. Go 层调整

### 8.1 Adapter 命名

当前结构：

```text
internal/inference/backend/mlx
internal/native/mlx
```

目标结构：

```text
internal/inference/backend/rwkvmobile
internal/native/rwkvmobile
```

`mlx` 变成 backend/provider 配置，而不是整个 adapter 的名字：

```go
rwkvmobile.NewBackend(rwkvmobile.Options{
    Provider: "mlx",
})
```

这个调整应在 C ABI facade 可用后进行，避免只做目录改名而没有改变依赖边界。

### 8.2 Conversation 层

Conversation 不应塞进 native adapter。建议增加：

```text
internal/conversation/
├── conversation.go
├── store.go
├── revision.go
└── restore.go
```

职责：

- 管理已提交 transcript；
- 组织 turn 事务；
- 保存与加载 session bundle；
- 判断 native State 是否兼容；
- 在需要时调用 Session prefill 重建；
- 向 CLI 提供 `/state` 和 `/history` 所需信息。

推理 Session 继续负责：

- recurrent State；
- token prefill；
- generation；
- reset、cancel；
- provider State export/import；
- State status 和性能统计。

### 8.3 需要补充的 Go 接口

当前 `Session` 还缺少明确的 replay 原语。这个里程碑增加：

```go
type Session interface {
    Generate(context.Context, GenerateRequest, EventSink) (GenerateResult, error)
    Prefill(context.Context, PrefillRequest, ProgressSink) (PrefillResult, error)
    CountTokens(context.Context, TokenCountRequest) (int, error)
    Reset(context.Context) error
    // existing state methods...
}
```

`Prefill` 必须只推进 State，不采样、不产生 assistant 输出，并返回最终 token prefix revision。Conversation restore 不能通过“重新生成旧回答”来重建 State。

## 9. 实施顺序

### Milestone A：固定采用边界

- 将 RWKV Mobile 作为内部维护的固定 revision。
- 记录启用的 provider 和构建选项。
- 禁用 CLI 不使用的 server、TTS、vision 和其他可选组件。
- 为依赖增加确定的版本或 commit，避免构建时跟随 `master`。

验收：

- 当前 MLX CLI 构建和实模测试不回退。
- 最小构建不携带未使用功能。

### Milestone B：实现安全的 Runtime facade

- 增加 ABI version。
- 增加带 `user_data` 的同步 streaming callback。
- 不再让 Go adapter 依赖进程级全局 writer。
- 增加受控 cancel 和 destroy/join 顺序。
- 统一错误 code。
- 增加 provider Capability 查询。
- 对未实现 State 方法返回 `unsupported`，不能默认成功。
- 生成成功时为“输入前缀 + 完整输出 token”注册 checkpoint；不能继续依赖当前只缓存 prompt prefix 的 raw completion 路径。

验收：

- 生成期间取消、关闭 Session、关闭 Model 和关闭 Runtime 都没有悬空线程。
- `go test -race` 下 callback 路由和生命周期测试通过。

### Milestone C：补齐 Conversation 与多轮提交

- CLI 持有完整 transcript。
- 每轮生成采用候选 turn，成功后才提交。
- revision 绑定 transcript 和模型语义指纹。
- 取消后不提交残缺消息。
- 增加 `clean/generating/dirty/rebuilding` 状态。
- dirty Session 在下一轮前自动重建。

验收：

- 至少连续五轮对话能引用早先信息。
- generation sink error 和取消不会污染下一轮上下文。
- `/history` 与实际提交内容一致。

### Milestone D：State 保存与恢复

- 增加 `Prefill`/replay 原语。
- 实现 session bundle 和原子存储。
- 实现 `/state`、`/save`、`/load`、`/reset`。
- provider 支持时保存 native State；不支持时只保存 logical State。
- 加载时验证所有指纹，并在需要时 replay。

验收：

- 退出进程后能够从 bundle 恢复同一对话上下文。
- 删除可选 `state.bin` 后仍能从 transcript 恢复。
- 模型或 tokenizer 不匹配时明确拒绝加载。
- 损坏的 transcript 或 State checksum 不会被使用。

### Milestone E：CLI 收尾与三端准备

- `Ctrl-C` 区分“取消生成”和“退出 REPL”。
- 加入结构化错误和加载/重建进度。
- 输出 provider、模型指纹和 State 恢复方式。
- 将平台差异限制在 build script 和 native packaging。
- 建立 macOS、Windows、Linux 的最小编译矩阵；这个阶段不要求三个平台都已有高性能 provider。

验收：

- CLI 和 Conversation 层没有 `mlx` 专有类型。
- 没有 prompt、输出或 native 日志串流混淆。
- 普通测试不依赖真实大模型；实模测试可以显式启用。

## 10. 短期完成定义

满足以下全部条件后，这个小目标才算完成：

1. 用户通过一个命令加载模型并进入 REPL。
2. 同一个进程内至少五轮对话保持正确上下文。
3. 每一轮只有在生成成功后才提交 transcript 和 State revision。
4. 用户能查看、重置、保存和加载会话。
5. 保存文件始终包含 transcript，native State 只是可选附件。
6. 不支持 native State export 的 provider 能通过 transcript replay 恢复。
7. 取消或输出失败后不会继续使用未知 State。
8. 加载不兼容或损坏的 State 会失败，而不是静默降级为错误上下文。
9. CLI 不直接调用 RWKV Mobile C API。
10. Runtime、Model、Session 和 generation 的释放顺序有自动化测试。
11. mock contract tests、普通 Go tests 和 MLX 实模测试通过。
12. 文档中的命令和实际 CLI 行为一致。

## 11. 这个里程碑明确不做

- 工具调用与 Agent step loop；
- RAG、长期记忆和上下文摘要；
- 桌面 UI；
- 多用户或多进程会话服务；
- 多 Session 并发生成；
- batch、vision、TTS；
- 为了表面统一而实现所有 provider 的 State 二进制互转；
- 在短期目标中接入新的推理后端。

这些功能以后都建立在本里程碑形成的 Conversation、Session 和 Runtime 边界之上。

## 12. 下一步

下一次实现从 **Milestone B：安全的 Runtime facade** 开始，第一组改动控制在以下范围：

1. 在 `internal/native/rwkvmobile` 建立通用 bridge。
2. 增加带 `user_data` 的同步 generation callback。
3. 增加 ABI version、稳定错误和基础 Capability。
4. 保持底层仍只启用 MLX provider。
5. 迁移现有 MLX adapter，并让现有测试全部通过。

Milestone A 当前已经具备“固定 submodule revision”和“MLX 最小构建”两个基础条件；剩余的依赖锁定与构建裁剪可以随 facade 构建改动一起完成。

完成这一组后，再开始 Conversation 和 State 恢复；不要把 C ABI 改造、会话存储和 REPL 命令一次性混在同一个提交中。
