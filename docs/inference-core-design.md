# RWKV-Agent 跨平台推理核心设计

状态：Draft v0.2

适用范围：RWKV-Agent 在 macOS、Windows、Linux 三个桌面端的本地原生推理层

目标读者：推理后端、Agent Harness 与桌面宿主的开发者

## 1. 结论

RWKV-Agent 的推理核心应当是一个嵌入 Go 进程的、后端无关的状态化模型服务层。它向 Agent Harness 暴露稳定的 Go 接口，向下适配 MLX、llama.cpp，以及后续确有桌面价值的原生后端。

第一版设计作出以下决定：

1. **Agent 只依赖统一推理接口，不感知 MLX、GGUF、Metal 或 cgo。**
2. **模型、会话和生成是三个独立生命周期。** 模型权重可共享；RWKV 运行时 State 归会话独占。
3. **消息历史和精确 token 前缀是事实源，State 是可丢弃、可重建的加速产物。**
4. **State 是一等能力，但不是假定能跨后端移植的通用字节串。**
5. **所有生成都流式输出，并具有明确的取消、完成原因和提交语义。**
6. **公共接口提供一致的最低语义，性能特性通过 Capability 显式声明。**
7. **Prompt 模板、tokenizer 和 State 必须绑定版本与指纹，禁止静默混用。**
8. **推理核心不执行工具。** 工具注册、权限、Agent step loop、记忆与 RAG 属于 Agent Harness。
9. **第一阶段保持进程内原生推理。** 不依赖 Python、外部 HTTP 推理服务或用户另行安装的运行时。

## 2. 目标和非目标

### 2.1 目标

- 同一套 Agent Harness 可以运行在 macOS、Windows、Linux。
- 同一套语义可以由不同推理后端实现，并允许自动选择最合适的后端。
- 支持文本聊天、原始续写、流式生成、取消、token 计数和性能统计。
- 正确表达 RWKV 的 recurrent State、初始 State、历史 checkpoint 和前缀缓存。
- 支持多个逻辑会话共享一个已加载模型。
- 支持从消息历史安全地重建会话，不把某个后端的缓存当作唯一数据。
- 为后续结构化输出、批处理、多模态和桌面 GPU 加速留出扩展点。
- 能通过统一的 contract tests 判断一个新后端是否符合核心语义。

### 2.2 非目标

以下内容不属于推理核心：

- 工具的发现、注册、执行和权限审批。
- Agent 的最大步数、反思、重试、规划或多 Agent 调度。
- 长期记忆、向量数据库、RAG 和上下文选择策略。
- 对话数据库、用户账户和云同步。
- WebView/WASM UI、窗口管理和系统托盘。
- 模型下载商店及其产品交互。
- 将 rwkv-mobile 的全部 C API 原样暴露给上层。

推理核心可以接收 `tool` 角色消息和结构化输出约束，但不应直接执行任何工具。

## 3. 分层与依赖方向

```text
Desktop Host / CLI
              │
        Agent Harness
   tools · memory · step loop
              │
      inference public API
              │
 ┌────────────┴─────────────┐
 │ prompt / tokenizer       │
 │ model manager            │
 │ session + state manager  │
 │ scheduler + event stream │
 └────────────┬─────────────┘
              │
      backend adapter API
              │
 ┌────────┬──────────┬────────────────────┐
 │ MLX    │ llama.cpp│ future desktop ... │
 └────────┴──────────┴────────────────────┘
              │
        native model runtime
```

依赖只能向下：

- Agent Harness 可以依赖 `inference`。
- `inference` 可以依赖私有的 backend adapter。
- backend adapter 可以依赖 cgo、C/C++ 和平台资源。
- `inference` 不得反向依赖 Agent、UI 或某个具体 backend 包。

建议第一阶段使用以下包布局：

```text
internal/inference/
├── core.go              # Core、Model、Session 公共契约
├── types.go             # 消息、请求、事件、结果
├── capability.go
├── errors.go
├── prompt/
├── state/
└── backend/
    ├── backend.go       # 私有 adapter 契约
    ├── mock/            # contract tests
    └── rwkvmobile/      # 通用 cgo bridge，不以 mlx 命名
```

接口稳定后，如果需要允许仓库外部扩展，再考虑从 `internal/inference` 提升为公开包。第一版不承诺第三方 Go API 稳定性。

## 4. 核心对象与生命周期

### 4.1 Core

`Core` 负责发现可用后端、探测模型、选择后端和加载模型。它拥有进程级调度器与原生 Runtime。

保证：

- 并发调用安全。
- `Close` 幂等。
- 后端发现不要求先加载模型。
- `auto` 选择必须可解释，结果包含选择原因。
- 不允许因为某个可选后端初始化失败而使全部后端不可用。

### 4.2 Model

`Model` 表示已经加载的权重、tokenizer、Prompt 模板和 backend 实例。

保证：

- 模型元数据加载后不可变。
- 多个 Session 可以共享权重。
- `Model.Close` 前必须结束或关闭其 Session。
- 模型格式与 backend 不匹配时应在加载阶段失败。
- 模型指纹必须能稳定识别权重、架构和量化配置。

### 4.3 Session

`Session` 表示一个有顺序的、状态化的推理上下文。

保证：

- 每个 Session 独占其逻辑 State。
- 同一 Session 同时最多有一个修改 State 的操作。
- 对同一 Session 并发调用 `Generate` 返回 `ErrBusy`，而不是产生数据竞争。
- `Reset` 回到零 State 或该 Session 配置的初始 State。
- Session 记录自己当前对应的 token 前缀指纹和 State revision。
- Session 不把 C 指针、backend state tree 节点或平台文件路径暴露给 Agent。

多 Session 是否能真正并行，由 backend Capability 决定。当前 rwkv-mobile 回调没有 user-data，现有桥接必须进程级串行生成；第一版应如实报告 `MaxConcurrentGenerations = 1`，由调度器排队，而不是让上层偶然依赖这个限制。

## 5. 第一版统一 Go 接口

以下代码是接口方向，不要求第一轮实现逐字一致。实现时应优先保持语义，避免为了形式提前抽象。

### 5.1 Core 与后端发现

```go
package inference

type Core interface {
    Backends(context.Context) ([]BackendInfo, error)
    ProbeModel(context.Context, ModelSource) (ModelInfo, error)
    LoadModel(context.Context, LoadRequest, ProgressSink) (Model, error)
    Close() error
}

type BackendInfo struct {
    ID           BackendID
    DisplayName  string
    Platform     string
    Device       DeviceInfo
    Formats      []ModelFormat
    Capabilities Capabilities
    Available    bool
    UnavailableReason string
}

type LoadRequest struct {
    Source           ModelSource
    Backend          BackendID       // "auto" 或显式 backend
    Device           DeviceSelector
    InitialState     *StateSource
    MemoryBudget     ByteSize
    BackendOptions   map[string]string
}
```

`BackendOptions` 只作为暂时的后端逃生舱。常用配置应提升为类型化字段，Agent 不应自行拼装 backend 专有参数。

### 5.2 Model

```go
type Model interface {
    Info() ModelInfo
    Capabilities() Capabilities
    Tokenizer() Tokenizer
    NewSession(context.Context, SessionOptions) (Session, error)
    Close() error
}

type ModelInfo struct {
    ID                 ModelID
    Fingerprint        string
    Architecture       string
    ArchitectureVersion int
    Format             ModelFormat
    Precision          string
    Quantization       string
    ParameterCount     uint64
    VocabularySize     int
    ContextPolicy      ContextPolicy
    Tokenizer          TokenizerInfo
    PromptTemplate     PromptTemplateInfo
    Backend            BackendID
}
```

RWKV 没有 Transformer 意义上的固定 KV cache 窗口，但这不代表上下文无限且无成本。`ContextPolicy` 应描述：

- 后端能接受的最大单次 prefill token 数。
- Agent 建议的历史压缩阈值。
- State 精度和长期递推可能带来的质量限制。
- backend 或设备的内存限制。

### 5.3 Session

```go
type Session interface {
    Generate(context.Context, GenerateRequest, EventSink) (GenerateResult, error)
    Prefill(context.Context, PrefillRequest, ProgressSink) (PrefillResult, error)
    Reset(context.Context) error

    StateInfo() SessionStateInfo
    ExportState(context.Context, StateWriter, ExportStateOptions) (StateDescriptor, error)
    ImportState(context.Context, StateReader, ImportStateOptions) (StateDescriptor, error)
    Fork(context.Context) (Session, error)

    Stats() SessionStats
    Close() error
}
```

其中：

- `Generate`、`Prefill`、`Reset` 是统一语义。
- `ExportState`、`ImportState` 和 `Fork` 可以返回 `ErrUnsupported`，并通过 Capability 预先声明。
- `StateReader`/`StateWriter` 应基于流，而不是强制要求文件路径。仅支持文件 API 的 native adapter 可在内部使用受控临时文件。
- `Fork` 表示从完全相同的 prefix State 分叉两个独立会话；它不是合并 State。

### 5.4 Tokenizer 与 Prompt 模板

```go
type TokenID int32

type Tokenizer interface {
    Info() TokenizerInfo
    Encode(context.Context, string) ([]TokenID, error)
    Decode(context.Context, []TokenID) (string, error)
    CountText(context.Context, string) (int, error)
    CountMessages(context.Context, []Message, PromptOptions) (int, error)
}

type PromptCompiler interface {
    Info() PromptTemplateInfo
    Compile(context.Context, []Message, PromptOptions) (CompiledPrompt, error)
}

type CompiledPrompt struct {
    Text             string
    Tokens           []TokenID
    TokenFingerprint string
    TemplateID       string
}
```

Prompt 模板属于模型语义，不属于 CLI。它应由推理核心统一执行，因为以下内容都会改变 State：

- role 名称和分隔符；
- BOS/EOS；
- reasoning 标记；
- tool call/tool result 的序列化格式；
- 是否附加 assistant generation prompt；
- 文本归一化与 tokenizer 版本。

模板必须有稳定的 `TemplateID` 和版本。模板改变后，旧 State 不得继续使用。

## 6. 消息、输入与输出

### 6.1 消息格式

```go
type Role string

const (
    RoleSystem    Role = "system"
    RoleUser      Role = "user"
    RoleAssistant Role = "assistant"
    RoleTool      Role = "tool"
)

type Message struct {
    Role       Role
    Name       string
    ToolCallID string
    Parts      []ContentPart
}

type ContentPart struct {
    Kind     ContentKind
    Text     string
    Media    *MediaRef
}
```

第一版只要求 `text`。图片、音频等 Part 必须由 Capability 控制；不支持时返回 `ErrUnsupported`，不能悄悄丢弃。

Agent 每次生成应传入完整的、语义上的消息历史。推理核心编译为精确 token 前缀，并使用 Session State 或 prefix cache 加速。这使得：

- 对话可以从数据库重建；
- 编辑历史后能检测 prefix 不匹配；
- State 损坏或不兼容时可以重新 prefill；
- 不同 backend 可以共享逻辑会话，而不要求共享二进制 State。

### 6.2 生成请求

```go
type GenerateRequest struct {
    Messages       []Message
    Raw            *RawInput
    Prompt         PromptOptions
    Sampling       SamplingOptions
    Limits         GenerationLimits
    Stops          []StopSequence
    ResponseFormat ResponseFormat
    Commit         CommitPolicy
}

type SamplingOptions struct {
    Temperature      float32
    TopK             int
    TopP             float32
    PresencePenalty  float32
    FrequencyPenalty float32
    PenaltyDecay     float32
    Seed             *int64
}

type GenerationLimits struct {
    MaxOutputTokens int
}

type CommitPolicy string

const (
    CommitOnSuccess CommitPolicy = "on_success"
    CommitPartial   CommitPolicy = "partial"
)
```

约束：

- `Messages` 与 `Raw` 必须二选一。
- `RawInput` 用于续写和低层测试，不应用聊天模板。
- 默认 `CommitOnSuccess`。
- 同样的模型、token 前缀、SamplingOptions 和 seed 应尽可能得到可复现输出；若 backend 无法保证，应在 Capability 中声明。
- stop sequence 应允许文本或 token 序列。核心必须说明 stop 内容是否包含在输出中，第一版统一为“不包含”。
- penalty、seed 或 response format 不支持时返回 `ErrUnsupported`，不能静默忽略。

`ResponseFormat` 第一版至少支持纯文本。JSON Schema、grammar constrained decoding 是可选能力。工具调用协议可以基于它构建，但工具执行仍属于 Agent Harness。

### 6.3 流式事件

```go
type EventSink func(GenerationEvent) error

type GenerationEvent struct {
    Kind EventKind

    LoadProgress    *Progress
    PrefillProgress *Progress
    Delta           *OutputDelta
    Usage           *Usage
    Warning         *Warning
}

type OutputDelta struct {
    Channel OutputChannel
    Text    string
    Tokens  []TokenID
}

const (
    ChannelFinal     OutputChannel = "final"
    ChannelReasoning OutputChannel = "reasoning"
)
```

事件契约：

- 单次生成的事件严格有序，且不会并发调用 `EventSink`。
- 文本 delta 拼接后必须等于 `GenerateResult.Output`。
- token delta 是可选能力，不能为了提供 token 而重复输出文本。
- sink 返回错误等价于请求取消。
- `context.Context` 是唯一公共取消机制。
- prefill 和 decode 进度必须区分。
- 后端日志不得混入模型文本事件。
- reasoning 与 final 如果无法可靠分离，统一作为 final 文本输出，并发出 Capability/Warning；不能靠不稳定字符串猜测后伪装成可靠分段。

### 6.4 完成结果

```go
type GenerateResult struct {
    Output        string
    OutputTokens  []TokenID
    FinishReason  FinishReason
    Usage         Usage
    Timings       Timings
    Committed     bool
    StateRevision string
}

const (
    FinishStop      FinishReason = "stop"
    FinishLength    FinishReason = "length"
    FinishCancelled FinishReason = "cancelled"
    FinishError     FinishReason = "error"
)
```

Agent 不能通过“error 是否为 nil”猜测 State 是否已提交，必须读取 `Committed`。

## 7. RWKV State 模型

### 7.1 为什么 State 是一等概念

RWKV 在逐 token 推理时更新 recurrent State。它概括了已经处理的 token 前缀，与 Transformer 的 KV cache 形态不同，但具有相似的会话加速作用。

要继续生成，通常至少需要：

- 与模型架构和权重匹配的 recurrent State；
- 该 State 所代表的精确 token 前缀；
- 对应该前缀末端的 logits，或重新计算 logits 的能力；
- 相同的 tokenizer 与 Prompt 模板语义。

State 不能被当作可读对话记录，也不能从 State 可靠还原原始消息。

### 7.2 四类容易混淆的 State

| 类型 | 用途 | 是否是事实源 | 典型生命周期 |
|---|---|---:|---|
| Logical transcript | 用户、助手、工具消息 | 是 | 持久化、跨后端 |
| Initial State | persona、领域或训练得到的初始状态 | 否 | 模型/Session 初始化 |
| Runtime checkpoint | 某个精确 token 前缀后的 recurrent State | 否 | Session 恢复、分叉 |
| Prefix cache | 多个常用 token 前缀的 State tree/cache | 否 | 进程内性能优化 |

当前 rwkv-mobile 已经存在这些底层能力：

- `.pth`/`.rmpack` 初始 State；
- 将历史前缀 State、token IDs 和 logits 保存到磁盘；
- 将历史 State 加载回内存；
- 按 token 前缀匹配最深 checkpoint；
- 清零 State；
- 为已知 prompt 做预填充缓存。

统一接口不应照搬这些函数名，而应把它们组织为 Session、checkpoint 和 cache 三套清晰语义。

### 7.3 State 兼容性

导出的 State 必须带有可验证的 envelope：

```text
magic
format_version
state_codec
model_fingerprint
architecture + version
precision / quantization
backend_id + backend_state_version
tokenizer_fingerprint
prompt_template_id
initial_state_fingerprint
prefix_token_count
prefix_token_hash
last_logits_encoding
payload_length
payload_checksum
payload
```

导入时逐项验证。任何关键字段不匹配都返回 `ErrIncompatibleState`，不得“尽量加载”。

默认假设：

- State **不跨模型**。
- State **不跨 tokenizer**。
- State **不跨 Prompt 模板版本**。
- State **不保证跨 backend**。
- 即使同一 backend，不同量化、精度或 state codec 版本也可能不兼容。
- transcript 可以跨 backend；不兼容时从消息重新编译 token 并 prefill。

未来若两个 backend 证明 State 表示完全兼容，可以声明相同的 `state_codec`，但必须有交叉恢复测试，不能仅凭 tensor shape 判断。

### 7.4 State revision 与前缀一致性

每个 Session 持有：

```text
revision
prefix_token_hash
prefix_token_count
template_id
model_fingerprint
state_status = clean | generating | dirty | closed
```

生成开始前：

1. 编译请求中的完整消息历史。
2. 对 token 前缀计算稳定 hash。
3. 若与当前 Session revision 匹配，直接继续。
4. 若请求是当前前缀的扩展，恢复 checkpoint 并只 prefill 后缀。
5. 若历史被编辑或分叉，查找最长 prefix cache。
6. 没有兼容 cache 时，从零 State 或 Initial State 重新 prefill。

这样 Session 不会因为上层少传或多传一条消息而静默使用错误 State。

### 7.5 生成的事务语义

生成会逐 token 修改 RWKV State，因此取消和失败必须有明确策略。

默认 `CommitOnSuccess`：

1. 生成前保存可恢复 checkpoint，或记录可重建的已提交 prefix。
2. 正常 stop/length 完成后，注册新 checkpoint 并增加 revision。
3. 取消、sink error 或 backend error 时，恢复生成前 checkpoint。
4. 如果 backend 不支持廉价恢复，则将 Session 标记为 `dirty`。
5. dirty Session 在下一次生成前必须从 transcript 重建，不能继续使用未知 State。

`CommitPartial` 用于用户点击停止但希望保留已经生成的内容：

- 只有 backend 能确认 State 与返回的完整 token 序列一致时才允许提交。
- 结果必须返回 `Committed=true` 和新的 revision。
- Agent Harness 负责把 partial assistant message 写入 transcript。

### 7.6 Initial State

Initial State 是 Session 的起点，而不是普通聊天消息。

规则：

- 在 `NewSession` 时选择，Session 建立后不能静默替换。
- 其指纹是所有 runtime checkpoint 兼容性的一部分。
- `Reset` 回到 Initial State；没有 Initial State 时回到零 State。
- Initial State 加载失败不得退化为零 State 后继续运行。
- `.pth` 和 `.rmpack` 是输入格式细节，不进入 Agent API；核心通过 `StateSource` 表达。

### 7.7 Prefix cache

Prefix cache 用于复用 system prompt、persona、固定工具说明或相同对话前缀。

它应具备：

- key 包含模型、tokenizer、模板、Initial State 和 token hash；
- 内存预算；
- LRU/使用次数等可预测的淘汰策略；
- 引用计数，不能淘汰正在生成使用的 State；
- 命中、未命中、占用字节和 checkpoint 数统计；
- 一键清空；
- 视为优化，清空后不影响正确性。

不应向 Agent 暴露 backend state tree 的节点或生命周期计数。

## 8. Capability 模型

不能用“所有 backend 的最小交集”限制整个系统，也不能假定每个 backend 支持所有操作。

```go
type Capabilities struct {
    TextGeneration          Support
    StreamingText           Support
    Cancellation            Support
    StatefulSessions        Support
    StateExport             Support
    StateImport             Support
    StateFork               Support
    PrefixCache             Support
    TokenStreaming          Support
    DeterministicSeed       Support
    BatchGeneration         Support
    Logits                  Support
    JSONSchema              Support
    Vision                  Support
    Audio                   Support

    SupportedBatchSizes     []int
    MaxConcurrentGenerations int
}

type Support struct {
    Available bool
    Emulated  bool
    Detail    string
}
```

其中：

- `Available=true, Emulated=false`：backend 原生支持。
- `Available=true, Emulated=true`：核心通过重建、缓冲或其他方式提供相同语义。
- `Available=false`：调用返回 `ErrUnsupported`。

第一版每个可发布 backend 必须满足：

- 文本生成；
- 文本流式输出；
- context 取消；
- token 计数；
- Session reset；
- 完成原因；
- usage/timing；
- 至少一个 Session。

State export/import、Fork、batch、logits、grammar 和多模态是可选能力。

## 9. 后端选择与平台策略

### 9.1 `auto` 选择

自动选择必须是确定且可解释的。建议顺序：

1. 过滤当前平台不可用的 backend。
2. 过滤不支持模型格式或架构的 backend。
3. 过滤不满足请求 RequiredCapabilities 的 backend。
4. 根据用户偏好、设备、预计内存和性能排序。
5. 返回选择结果以及被跳过 backend 的原因。

不能因为系统上存在 Metal/Vulkan 就假定模型格式兼容。

### 9.2 目标矩阵

| 平台 | 第一可用后端 | 优化后端 | 典型模型格式 |
|---|---|---|---|
| macOS arm64 | llama.cpp CPU | MLX / Metal | GGUF、MLX safetensors |
| Windows x64 | llama.cpp CPU | llama.cpp / Vulkan | GGUF |
| Linux x64 | llama.cpp CPU | llama.cpp / Vulkan | GGUF |

当前跨平台目标到此为止：macOS arm64、Windows x64、Linux x64。Android、iOS 和 Web 端不属于本设计范围，也不应影响第一版公共接口。

### 9.3 构建边界

- 公共 `inference` 包不能有平台 build tag。
- build tag 只存在于 backend adapter 和 native 链接层。
- MLX 资源、动态库、Vulkan 库等通过内部 `AssetLocator` 查找。
- 运行时必须能报告缺失的是模型、动态库、驱动还是资源 bundle。
- backend 的 C/C++ 错误码统一转换为类型化 Go Error，同时保留 native code 供诊断。
- Go 层应只有一个通用 `rwkvmobile` adapter，backend 名称是加载配置，不再创建一个公开的 `mlx.Runtime` 抽象。

## 10. 错误模型

```go
type ErrorCode string

const (
    CodeInvalidArgument    ErrorCode = "invalid_argument"
    CodeUnavailable        ErrorCode = "unavailable"
    CodeUnsupported        ErrorCode = "unsupported"
    CodeIncompatibleModel  ErrorCode = "incompatible_model"
    CodeIncompatibleState  ErrorCode = "incompatible_state"
    CodeCorruptState       ErrorCode = "corrupt_state"
    CodeResourceExhausted  ErrorCode = "resource_exhausted"
    CodeBusy               ErrorCode = "busy"
    CodeCancelled          ErrorCode = "cancelled"
    CodeIO                 ErrorCode = "io"
    CodeBackendFailure     ErrorCode = "backend_failure"
    CodeClosed             ErrorCode = "closed"
)

type Error struct {
    Op         string
    Code       ErrorCode
    Backend    BackendID
    NativeCode int
    Retryable  bool
    Err        error
}
```

规则：

- 调用方使用 `errors.Is`/`errors.As` 判断，不解析错误文本。
- 用户主动取消返回 `context.Canceled` 语义。
- 模型或 State 不兼容不是 retryable。
- OOM/资源不足与模型格式错误分开。
- backend 崩溃风险操作应尽量在加载或探测阶段提前验证。
- 日志可以包含详细路径，面向 UI 的 Error 不应泄漏不必要的本地敏感路径。

## 11. 调度、线程与资源

### 11.1 并发

- `Core` 与 `Model` 可被并发读取。
- Session 修改操作串行。
- scheduler 根据 `MaxConcurrentGenerations` 管理 backend 队列。
- 排队也必须响应 context 取消。
- 一个 Session 的回调不得在持有会阻塞 `Stop`/`Close` 的锁时调用。
- native callback 无 user-data 时，在 bridge 层建立请求注册表或明确串行，不使用不受保护的全局 writer。

### 11.2 内存

资源统计至少包含：

- 模型权重估计；
- 当前 Session State；
- prefix cache；
- 临时 logits/output buffer；
- backend 报告的设备内存。

超出预算时优先淘汰可重建 prefix cache，再拒绝新 Session；不能无界积累历史 State tree。

### 11.3 关闭

关闭顺序：

1. 停止接受新请求；
2. 取消或等待进行中的生成；
3. 关闭 Session；
4. 释放模型；
5. 释放 native Runtime 和平台资源。

所有 `Close` 幂等。结束后调用返回 `CodeClosed`，不能触发 use-after-free。

## 12. Agent Harness 所需但不属于推理核心的能力

推理核心必须为 Agent 提供足够的原语，但保持边界：

| 能力 | 推理核心 | Agent Harness |
|---|---:|---:|
| 消息到 token 的确定性编译 | 是 | 否 |
| recurrent State 与 prefix cache | 是 | 否 |
| 流式生成与取消 | 是 | 消费事件 |
| tool 角色消息 | 支持序列化 | 构造与保存 |
| JSON/grammar 约束 | 可选推理能力 | 选择 schema |
| 工具注册和执行 | 否 | 是 |
| 工具权限与用户确认 | 否 | 是 |
| step loop / max steps | 否 | 是 |
| 对话持久化 | State 可导出 | transcript 是主记录 |
| 上下文裁剪和摘要策略 | 提供 token 计数 | 是 |
| 重试策略 | 提供错误分类 | 是 |

建议 Agent Harness 永远持久化 transcript。导出的 State 作为相同 revision 的附件保存；State 缺失、过期或不兼容时丢弃并从 transcript 重建。

## 13. 可观测性

推理核心应提供结构化指标，不依赖解析 native 日志：

- 模型加载进度和耗时；
- prompt token、生成 token；
- time to first token；
- prefill tokens/s；
- decode tokens/s；
- prefix cache hit/miss；
- State export/import 大小与耗时；
- 当前排队请求数；
- 当前 Session 数；
- backend、设备和模型指纹；
- finish reason；
- fallback/rebuild 次数。

日志与生成输出必须分离。默认日志不记录完整 prompt、工具结果和模型输出；调试模式也应提供脱敏开关。

## 14. Contract tests

每个 backend adapter 必须通过相同测试集。

### 14.1 基础行为

- 模型加载、关闭和重复关闭。
- 空输入与非法 sampling 参数。
- 流式 delta 拼接等于最终输出。
- `MaxOutputTokens` 和 stop sequence。
- context 取消和 sink error。
- token 计数与 Prompt 编译一致。
- 不支持能力返回 `ErrUnsupported`。
- 后端日志不会进入文本流。

### 14.2 State 行为

- Reset 后相同 prefix + seed 得到相同结果。
- 同一 checkpoint 导出再导入后继续生成一致。
- 模型指纹不匹配时拒绝 State。
- tokenizer/template/Initial State 不匹配时拒绝 State。
- State checksum 损坏时返回 `ErrCorruptState`。
- 历史编辑后不会错误复用旧 State。
- 取消后正确 rollback，或 Session 被标记 dirty 并在下次重建。
- Fork 后两个 Session 独立修改。
- prefix cache 被清空后结果仍正确。

### 14.3 工程质量

- `go test -race` 覆盖 mock backend 和 scheduler。
- 并发创建/关闭 Session。
- 生成期间关闭的竞态。
- 长时间循环生成后的内存增长。
- CI 至少编译 macOS arm64、Windows x64、Linux x64。
- 有模型的硬件集成测试可按 nightly/manual 运行；普通单元测试不依赖大模型。

## 15. 分阶段实施

### Phase 1：统一契约和可测试骨架

- 创建 `internal/inference` 类型和接口。
- 创建 deterministic mock backend。
- 建立 contract test suite。
- CLI 通过统一接口运行 mock。

验收：Agent/CLI 代码中没有 `mlx` 类型。

### Phase 2：迁移现有 MLX 链路

- 将当前 cgo 代码移入通用 `backend/rwkvmobile` adapter。
- MLX 作为一个 backend 配置注册。
- 保持当前真实模型性能和输出能力。
- 修正全局 callback 的调度边界。

验收：现有 MLX 集成测试通过，CLI 使用 `--backend auto|mlx`。

### Phase 3：Session 与 State

- 完整消息编译和 token prefix hash。
- Reset、revision、dirty/rebuild。
- Initial State。
- State export/import envelope。
- prefix cache 预算和统计。

验收：State contract tests 在 mock 和 MLX 上通过。

### Phase 4：第二后端与桌面跨平台

- 接入 llama.cpp/GGUF。
- Windows/Linux CPU 构建。
- macOS 上完成 MLX 与 llama.cpp 自动选择。
- 建立多平台 CI 和分发目录。

验收：同一个 CLI 和同一组 contract tests 在三种桌面系统运行。

### Phase 5：Agent Harness

- transcript 和会话持久化。
- tool schema、解析与权限。
- step loop 和取消。
- 将 State 作为 transcript revision 的可选加速附件。

## 16. 第一轮实现时必须避免的错误

- 不要把当前 `mlx.Runtime` 直接改名为 `inference.Runtime` 后继续硬编码 MLX。
- 不要让 Agent 保存 native 指针或 backend state tree 节点。
- 不要只保存 State 而不保存 transcript。
- 不要在 State 不兼容时静默从零开始并假装恢复成功。
- 不要让每个 backend 各自实现一套 Prompt 模板。
- 不要静默忽略 sampling、seed、stop 或 response format。
- 不要把生成文本、reasoning、native 日志混在同一字符串回调里。
- 不要假定“加载了同一个权重文件”就意味着跨 backend State 兼容。
- 不要先做 UI 再让 UI 直接绑定某个 backend。
- 不要为了接口统一而隐藏关键性能限制，例如全局串行生成。

## 17. 待验证问题

以下问题需要在实现阶段通过代码或集成测试回答：

1. rwkv-mobile 的各 backend 分别支持哪些 State serialize/deserialize 能力？
2. llama.cpp backend 的 GGUF State 能否稳定导出，还是只能依靠 transcript 重建？
3. MLX State 的实际内存大小、复制成本和 Fork 成本是多少？
4. 当前 generation callback 是否能在上游增加 user-data，消除进程级全局 writer？
5. reasoning/final 是否有可靠 token 边界，而不是只能解析文本标记？
6. 不同 backend 对同一 tokenizer 和 Prompt 模板的 token 结果是否完全一致？
7. 长对话 recurrent State 的数值精度、量化和质量退化应如何进入 `ContextPolicy`？
8. `.rmpack` Initial State 的版本和权重兼容信息是否足够，需要在外层增加 manifest 吗？
这些问题不阻塞 Phase 1，但会影响 Capability 和 State codec 的具体实现。
