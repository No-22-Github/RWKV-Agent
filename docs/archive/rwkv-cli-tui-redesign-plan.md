# RWKV CLI TUI 重做实施计划

状态：Implemented（Implementation Plan v1.1）

分析日期：2026-07-28

目标平台：macOS 15+ / Apple Silicon

说明：第 1–10 节记录最初的四路 dashboard v1.0 设计；第 11 节记录已落地的 v1.1
扩展，它取代了 v1.0 中“暂不支持鼠标”和“暂不超过四路”的阶段性限制。

关联文档：

- [RWKV Mobile macOS CLI 完整实施计划](rwkv-mobile-macos-cli-implementation-plan.md)
- [macOS CLI 实施与验证记录](macos-cli-implementation-validation.md)
- [跨平台推理核心设计](inference-core-design.md)

## 1. 背景与结论

当前 `rwkv-cli concurrent` 已经能真实触发 1–4 路连续批处理，也能报告
`max_native_batch=4`，但它不是一个合格的并发演示界面：

1. 四路生成结束后才统一输出，用户看不到并发发生的过程。
2. 每个 session 的 token、阶段、速度和完成时间没有实时可视化。
3. 输出按行堆叠，长文本混在一起，无法快速比较四路状态。
4. `fmt.Sprintf("[%d] %s", ...)` 把 session 编号写进了模型 prompt。编号本应只属于
   UI，这会导致四路输入语义不同，并可能诱导模型在回答中复述编号。
5. 并发路径直接管理 goroutine、Conversation、输出 buffer 和最终打印，命令入口承担了
   过多职责，后续难以单独测试 UI 或纯文本模式。
6. 当前 CLI 的加载、运行、取消和最终汇总缺少统一的视觉语言。

本计划决定：

- 使用 [Bubble Tea v2](https://github.com/charmbracelet/bubbletea) 作为 TUI 事件循环。
- 使用 [Lip Gloss v2](https://github.com/charmbracelet/lipgloss) 负责布局、边框、颜色和
  终端宽度计算。
- 第一阶段只把 `concurrent` 重做成全屏实时 dashboard。
- 第二阶段复用同一套 theme，改善 `run` 的加载提示、状态行和 REPL 外观，但不把普通
  REPL 强行改成全屏应用。
- 推理核心、Conversation 和 native runtime 不依赖任何 TUI 库。
- 非交互终端、重定向、CI 和脚本调用继续使用稳定的纯文本 renderer。

不选择 `tview` 作为第一方案。`tview` 的 Grid 和 TextView 很成熟，但当前数据模型是
高频流式事件，Bubble Tea 的单向消息循环更适合做状态聚合、resize 和声明式重绘。

## 2. 目标与非目标

### 2.1 P0 目标

1. 四路 session 在同一终端中实时流式输出。
2. 宽终端默认展示 2×2 pane；窄终端自动降级为单列。
3. 每个 pane 显示 session 状态、token 数、decode 速度、耗时和输出。
4. 顶部显示模型、provider、目标并发数和全局阶段。
5. 底部显示 native batch、总 token、aggregate tok/s 和按键提示。
6. 四路使用完全相同的用户 prompt，只使用不同 seed 制造独立采样。
7. UI 刷新不能显著拖慢 native generation。
8. `Ctrl-C` 能取消全部活动请求，并保证 Conversation 事务不提交残缺内容。
9. 非 TTY 环境自动使用纯文本输出，不发送 alternate-screen 或颜色控制序列。
10. 保持 `max_native_batch=4` 的真实模型验收结果。

### 2.2 P1 目标

1. `run` 命令使用同一套颜色、spinner、错误提示和性能摘要。
2. REPL prompt、命令帮助、State 信息和历史记录具有一致样式。
3. 支持在 dashboard 中切换当前 pane、滚动长输出和复制可见文本。
4. 支持完成后重新运行相同并发测试。

### 2.3 非目标

- 不修改 native scheduler、MLX provider 或连续批处理策略。
- 不让 Bubble Tea 类型进入 `internal/inference` 或 `internal/conversation`。
- 不在第一阶段实现鼠标操作、图表、Markdown 富文本渲染或图片协议。
- 不在第一阶段支持超过四路并发。
- 不把 benchmark 输出变成只能由人阅读的格式。
- 不在模型 prompt 中加入 session 编号、颜色标记或 UI 状态。

## 3. 目标交互

### 3.1 默认命令

```sh
./dist/rwkv-cli concurrent \
  --model ./build/real-model-test/model-mlx \
  --concurrency 4 \
  --concurrent-prompt "用一句话介绍 RWKV" \
  --max-tokens 128
```

当 stdout 和 stdin 都连接到支持交互的终端时，默认进入 TUI。重定向、pipe、CI 或
`TERM=dumb` 时自动进入 plain 模式。

新增参数：

```text
--ui auto|tui|plain
```

- `auto`：默认值，根据终端能力选择。
- `tui`：要求 TUI；终端不兼容时返回清晰错误。
- `plain`：强制稳定文本输出。

第一阶段不暴露 refresh rate、颜色 profile 和布局阈值等内部参数。

### 3.2 目标界面

```text
 RWKV G1 · MLX · Continuous Batch 4                         00:03.2

╭─ Session 1 · generating · 21.3 tok/s ─╮ ╭─ Session 2 · prefill · 46/71 ──────╮
│ RWKV 是一种基于 RNN 的语言模型，它…    │ │ 正在处理输入前缀…                    │
│                                       │ │                                      │
╰─ 48 tokens ───────────────────────────╯ ╰─ 0 tokens ───────────────────────────╯

╭─ Session 3 · done · 22.1 tok/s ───────╮ ╭─ Session 4 · generating · 19.8 tok/s ─╮
│ RWKV combines transformer-level…       │ │ RWKV 的主要特点包括恒定内存状态…      │
│                                        │ │                                      │
╰─ 39 tokens · 1.8s ─────────────────────╯ ╰─ 42 tokens ──────────────────────────╯

 native batch 4/4 · total 129 tokens · aggregate 63.2 tok/s
 Ctrl-C cancel all · q quit
```

界面信息分层：

- Header：模型短名、provider、目标 batch、总耗时。
- Pane title：session 编号、阶段、当前速度或 prefill 进度。
- Pane body：该 session 的独立输出，只保留 pane 可见区域的末尾内容。
- Pane footer：生成 token 数、完成耗时、finish reason。
- Global footer：`max_native_batch`、总 token、aggregate tok/s、快捷键。

### 3.3 响应式布局

| 终端条件 | 布局 |
|---|---|
| 宽度 ≥ 100、高度 ≥ 24、并发 4 | 2×2 |
| 宽度 ≥ 80、并发 2 | 1×2 |
| 宽度不足或高度不足 | 单列 pane |
| 无法为每个 pane 提供最小 6 行 | compact 列表 |
| 非 TTY / `TERM=dumb` | plain renderer |

布局必须使用终端 cell 宽度，不得使用字节数或 rune 数计算。中文、emoji 和 ANSI style
不能破坏边框对齐。

### 3.4 状态机

每个 session 只能处于以下状态之一：

```text
queued → prefill → generating → done
                              ↘ cancelled
                              ↘ error
```

全局状态：

```text
loading → preparing → running → completed
                             ↘ cancelling → cancelled
                             ↘ failed
```

颜色只作为辅助信息，所有状态必须同时有可读文字：

- queued：dim
- prefill：cyan
- generating：yellow
- done：green
- cancelled：magenta
- error：red

### 3.5 键盘语义

运行期间：

- `Ctrl-C`：取消全部活动生成，等待各 session 回滚并离开 TUI。
- `q` / `Esc`：与 `Ctrl-C` 相同，不允许留下后台 generation。
- `Tab` / 方向键：P1，切换 active pane。

全部完成后：

- `Enter` / `q` / `Esc`：退出 dashboard。
- TUI 退出 alternate screen 后打印一行稳定 summary。
- P1 可增加 `r`，使用相同参数重新运行。

不使用“第一次 Ctrl-C 只取消当前 pane”的语义。并发命令是一个整体测试，取消必须作用于
全部 session。

## 4. 架构设计

### 4.1 分层

```text
cmd/rwkv-cli
      │ parse flags / select renderer
      ▼
internal/cli/concurrent
      │ runner · lifecycle · aggregation
      ├──────────────► internal/cli/concurrent/plain
      │
      └──────────────► internal/tui/concurrent
                              │
                        Bubble Tea + Lip Gloss
      │
      ▼
internal/conversation
      │
internal/inference
      │
native runtime / MLX
```

依赖规则：

1. `cmd/rwkv-cli` 只做参数解析、runtime 装配和退出码映射。
2. concurrent runner 不导入 Bubble Tea 或 Lip Gloss。
3. TUI 只消费 runner event/snapshot，不直接调用 native runtime。
4. plain renderer 与 TUI renderer 消费同一套事件。
5. inference callback 不直接写 stdout、stderr 或 TUI。
6. renderer 失败或用户取消时，通过 context 取消整个 concurrent run。

### 4.2 建议目录

```text
internal/cli/concurrent/
├── runner.go
├── events.go
├── snapshot.go
├── summary.go
├── plain.go
└── runner_test.go

internal/tui/
├── theme.go
└── concurrent/
    ├── model.go
    ├── update.go
    ├── view.go
    ├── layout.go
    ├── messages.go
    └── view_test.go

internal/terminal/
├── detect.go
└── detect_test.go
```

如果实现后 `internal/cli/concurrent/plain.go` 过大，再拆成子包；第一版不为目录形式而
过度拆包。

### 4.3 Runner 数据契约

建议定义 UI 无关的数据类型：

```go
type SessionPhase string

const (
    PhaseQueued     SessionPhase = "queued"
    PhasePrefill    SessionPhase = "prefill"
    PhaseGenerating SessionPhase = "generating"
    PhaseDone       SessionPhase = "done"
    PhaseCancelled  SessionPhase = "cancelled"
    PhaseError      SessionPhase = "error"
)

type SessionSnapshot struct {
    Index          int
    Phase          SessionPhase
    Output         string
    PromptTokens   int
    OutputTokens   int
    PrefillDone    int
    PrefillTotal   int
    DecodeTPS      float64
    Elapsed        time.Duration
    FinishReason   inference.FinishReason
    Err            error
}

type RunSnapshot struct {
    Sessions       []SessionSnapshot
    StartedAt      time.Time
    Elapsed        time.Duration
    MaxNativeBatch int
    TotalTokens    int
    AggregateTPS   float64
    Done           bool
}
```

Renderer 不持有 `Conversation`、native session 或 callback。最终机器可读 summary 必须来自
runner，而不是重新解析 UI 字符串。

### 4.4 高频事件处理

不能为每个 token 强制完整重绘，也不能让终端刷新反向阻塞 MLX decode。

采用以下策略：

1. 每个 inference callback 将文本追加到该 session 的受保护 buffer。
2. callback 更新 token 数和最近一次活动时间。
3. callback 使用非阻塞 dirty notification 通知 UI；重复 dirty 信号允许合并。
4. TUI 以固定 tick（目标 20–30 FPS）读取 snapshot 并重绘。
5. `done`、`error`、`cancelled` 是可靠生命周期事件，不能丢弃。
6. pane 只渲染可见窗口的文本；runner 保留完整结果用于 plain summary 和测试。

这一设计保证：

- 输出字符不丢失。
- token callback 不等待终端绘制。
- 四路高频流式输出不会产生四套竞争 stdout 的 goroutine。
- `go test -race` 可以覆盖 buffer、snapshot 和取消路径。

### 4.5 Prompt 与 seed

必须删除：

```go
fmt.Sprintf("[%d] %s", index+1, options.concurrentPrompt)
```

四路都传入：

```go
options.concurrentPrompt
```

session 编号只存在于 `SessionSnapshot.Index`。为了展示不同采样结果，可以继续使用：

```go
seed := int64(42 + index)
```

同 prompt、不同 seed 是演示并发的正确语义。若用户显式指定固定 seed，后续可以定义
`base_seed + index`，但不在 P0 扩展新的 seed 参数。

### 4.6 终端能力与降级

`--ui auto` 至少检查：

1. stdin 和 stdout 是否为 character device。
2. `TERM` 是否为空或 `dumb`。
3. 是否处于已知 CI 环境。
4. 终端尺寸是否可读取。

自动检测失败时优先降级为 plain，而不是让推理失败。只有 `--ui tui` 才把不兼容终端
作为命令错误。

plain renderer 必须：

- 不输出 ANSI escape sequence。
- 保持每个 session 的完整输出边界。
- 最后打印现有 summary 字段。
- 支持 stdout 重定向和测试 snapshot。

### 4.7 stdout、stderr 与日志

- TUI 活动期间禁止其他 goroutine 写 stdout。
- 模型加载进度、native warning 和调试日志不得穿透 dashboard。
- 用户可见错误进入 TUI 状态；退出后向 stderr 输出简洁错误。
- `--ui plain` 时，session 输出写 stdout，运行状态和性能 summary 写 stderr。
- 如需调试 TUI，日志写到显式文件，不能默认创建日志。

## 5. UI 视觉规范

### 5.1 风格原则

- 以信息密度和对齐为主，不使用大面积 ASCII logo。
- 默认支持 dark/light terminal，不假定背景一定为黑色。
- 颜色自动降级到 ANSI 256/16 色。
- 每个 pane 使用相同边框，状态色只作用于标题和关键数字。
- 不使用 blink。
- 动画只用于 loading/prefill，且不得影响 benchmark。

### 5.2 文本处理

- 输出按 terminal cell 自动换行。
- pane 高度不足时显示最后 N 行，并在顶部显示 `…`。
- 不修改保存在 runner 中的原始模型输出。
- ANSI/control character 必须过滤或转义，防止模型输出破坏 TUI。
- `\r`、清屏序列、光标移动序列不得直接发送到终端。
- 中文标点、emoji、宽字符和组合字符纳入 golden test。

### 5.3 最终 summary

离开 TUI 后保留一行：

```text
Concurrent batch complete: sessions=4 max_native_batch=4 tokens=174 elapsed=2.114s aggregate=82.3 tok/s
```

该行继续作为人工验收和脚本 smoke test 的稳定契约。未来若需要严格机器输出，单独增加
`--json`，不让脚本解析彩色 pane。

## 6. 分阶段实施

### 阶段 0：建立行为基线

1. 为当前 `runConcurrent` 增加 fake model/Conversation 测试入口。
2. 固定 plain summary 的字段和错误语义。
3. 记录真实模型四路的 tokens、elapsed、aggregate 和 `max_native_batch`。
4. 增加“session 编号不得进入 prompt”的失败测试。

验收：

- 未加入 TUI 前，plain 行为已经可回归。
- 四路收到完全相同的用户文本。

### 阶段 1：提取 concurrent runner

1. 从 `cmd/rwkv-cli/main.go` 移出 goroutine、start barrier、buffer 和结果聚合。
2. runner 接收 model、conversation options、turn options、prompt 和 concurrency。
3. runner 暴露 snapshot/event，而不是打印字符串。
4. 现有输出改由 plain renderer 实现。
5. 保持命令行为不变。

验收：

- `cmd/rwkv-cli/main.go` 不再管理每个 session 的 buffer。
- fake backend 能稳定制造交错 token event。
- `go test -race ./...` 通过。

### 阶段 2：接入 Bubble Tea dashboard

1. 添加并固定 Bubble Tea v2、Lip Gloss v2 依赖版本。
2. 实现 header、pane、footer 和状态 theme。
3. 实现 2×2、单列和 compact layout。
4. 接入 runner snapshot 和 20–30 FPS 刷新。
5. 支持 resize、完成态和错误态。

验收：

- 四个 pane 在真实生成期间持续更新。
- resize 不崩溃、不越界、不破坏边框。
- 模型输出不能注入控制序列。

### 阶段 3：取消、TTY 与降级

1. 实现 `--ui auto|tui|plain`。
2. 接入统一 context cancellation。
3. PTY 下验证 `Ctrl-C`、`q`、`Esc`。
4. pipe、redirect、CI 和 `TERM=dumb` 验证 plain fallback。
5. 确保 alternate screen 在 panic/error/cancel 后恢复。

验收：

- 取消后没有残留 goroutine 或 native request。
- shell 光标、echo 和 terminal mode 正常恢复。
- 非 TTY 输出不含 ANSI。

### 阶段 4：真实模型与性能验收

使用：

```text
/Users/no22/Projects/Preen/models/rwkv7-g1h-1.5b-20260710-ctx10240.pth
```

以及已转换模型目录：

```text
/Users/no22/Projects/RWKV-Agent/build/real-model-test/model-mlx
```

验证：

1. 并发 1、2、4。
2. 中英文短输出和 256-token 长输出。
3. 运行中 resize。
4. 单 session 完成早于其他 session。
5. 一路取消/错误不会破坏其他 pane 状态展示。
6. 全局取消。
7. TUI 和 plain 的最终 token/result 一致。

性能门槛：

- `max_native_batch=4`。
- TUI 开启后 aggregate tok/s 相对 plain 中位数下降不超过 5%。
- UI CPU 占用不持续抢占模型计算。
- 终端刷新不成为 decode callback 的阻塞点。

### 阶段 5：普通 `run` 的轻量美化

在 concurrent dashboard 稳定后：

1. 复用 theme 显示模型加载 spinner 和完成状态。
2. 美化 REPL prompt、命令帮助和 `/state`。
3. 保持模型回答为普通可选择、可复制的终端文本。
4. 不使用 alternate screen，不改变现有多轮工作流。

此阶段与 concurrent TUI 分开验收，避免一次重写整个 CLI。

## 7. 测试计划

### 7.1 单元测试

- session/global 状态机合法迁移。
- 2×2、1×N、compact 布局尺寸。
- CJK、emoji、ANSI、超长单词和多行输出。
- terminal resize。
- pane 尾部裁剪。
- aggregate token、elapsed 和 tok/s 计算。
- plain renderer 无 ANSI。
- `--ui` 参数校验和 auto detection。

View 测试使用固定 terminal 宽高和 deterministic snapshot 做 golden test。Golden 内容避免
依赖当前终端颜色 profile。

### 7.2 并发与取消测试

- 四路 event 交错。
- 一路先完成。
- 一路 backend error。
- 生成中 context cancel。
- renderer 主动退出触发 cancel。
- dirty notification 合并。
- 慢 renderer 不丢输出。
- `go test -race ./...`。

### 7.3 PTY 集成测试

- 进入和退出 alternate screen。
- `Ctrl-C` 恢复终端。
- `q`/`Esc` 取消。
- `SIGTERM` 清理。
- resize signal。
- 完成后 summary 可见。
- redirected stdout 自动 plain。

### 7.4 真实模型测试

```sh
./dist/rwkv-cli concurrent \
  --model ./build/real-model-test/model-mlx \
  --concurrency 4 \
  --concurrent-prompt "分别用一句话解释 RWKV 的特点。" \
  --max-tokens 128
```

注意：四路实际输入必须完全相同；“分别”仅指四个独立采样结果，不在 prompt 中注入编号。

## 8. 风险与控制

| 风险 | 控制措施 |
|---|---|
| 每 token 重绘拖慢生成 | dirty 合并 + 固定帧率 snapshot |
| TUI 与日志争抢 stdout | TUI 期间单一 renderer 独占终端 |
| 模型输出控制字符破坏界面 | 渲染前过滤，不修改原始结果 |
| alternate screen 异常退出后未恢复 | defer cleanup、PTY crash/cancel 测试 |
| Bubble Tea v2 API 继续变化 | 固定依赖版本，集中封装在 `internal/tui` |
| TUI 侵入推理核心 | runner event/snapshot 为唯一边界 |
| 窄终端不可用 | compact layout 和 plain fallback |
| UI 标签污染 prompt | session index 只保留在 snapshot |
| 纯文本脚本兼容性破坏 | `--ui plain` 和稳定 summary 契约 |
| 四路输出过长导致内存增长 | pane 使用可见 ring，runner 按 max-tokens 保留完整结果 |

## 9. 完成定义

以下条件全部满足才算 TUI 重做完成：

- [x] `concurrent` 在正常终端默认显示实时 dashboard。
- [x] 四路相同 prompt、不同 seed，prompt 中没有 session 编号。
- [x] 四个 pane 能独立显示 prefill、generation、done/error/cancelled。
- [x] 2×2、单列和 compact layout 可用。
- [x] resize 和中英文宽字符显示正确。
- [x] `Ctrl-C`、`q`、`Esc` 能可靠清理全部生成。
- [x] TUI 异常退出后终端状态恢复。
- [x] 非 TTY 自动 plain，输出无 ANSI。
- [x] plain summary 字段保持稳定。
- [x] `go test ./...` 通过。
- [x] `go test -race ./...` 通过。
- [x] PTY 集成测试通过。
- [x] 指定 G1h 1.5B 模型真实四路生成通过。
- [x] `max_native_batch=4`。
- [x] TUI 相对 plain 的 aggregate tok/s 回退不超过 5%。
- [x] README 更新命令、快捷键、截图或录屏说明。

## 10. 建议的最终代码边界

完成后，`runConcurrent` 应缩减为类似以下流程：

```go
func runConcurrent(args []string) error {
    options, err := parseRunOptions("concurrent", args)
    if err != nil {
        return err
    }

    runtime, err := loadRuntime(...)
    if err != nil {
        return err
    }
    defer runtime.Close()

    runner := concurrent.NewRunner(runtime.model, ...)
    renderer, err := selectConcurrentRenderer(options.UI)
    if err != nil {
        return err
    }
    return renderer.Run(context.Background(), runner)
}
```

命令入口不再理解 pane、Bubble Tea message、token buffer 或布局；TUI 也不再理解 MLX、
native State 和 Conversation revision。这个边界是本次重做最重要的长期维护目标。

## 11. v1.1：8 路结果选择与 Conversation 续聊

v1.1 已完整落地：

- [x] `--concurrency` 开放 1–8，runtime 按实际并发数分配 active batch。
- [x] 8 路在标准宽度使用 2×4，超宽终端使用 4×2，并保留单列/compact 降级。
- [x] 所有初始窗口使用相同 prompt 和解码参数；只有独立 seed 不同。
- [x] 修复动态 prefill 只保护 slot 0 导致的 State 交叉污染。
- [x] 真实模型在 `top-k=1` 下验证 8 个输出逐字相同，`max_native_batch=8`。
- [x] 初始生成结束后保留每个 pane 对应的 `Conversation` 和 native State。
- [x] 鼠标点击任意 pane 后可在 footer 输入追问，回答继续流入原 pane。
- [x] 无鼠标时可用 Tab/方向键选择，再按 Enter 进入输入。
- [x] 每轮完成后自动保持在该 Conversation，可连续追问。
- [x] 续聊取消不提交残缺 turn，下一轮仍从最后一个已提交 revision 继续。
- [x] runner `Close`、rerun 和 TUI 退出会按序关闭全部保留的 Conversation。
- [x] PTY 测试覆盖鼠标协议、输入、流式续聊、alternate-screen 恢复和竞态检测。
- [x] 真实模型验证 8 路生成后点击 Session 3 并在同窗续聊。

v1.1 仍保持原边界：TUI 只消费 runner snapshot；Conversation 事务和 native State
生命周期不进入 Bubble Tea 层。点击 pane 只是选择已有会话，不会复制文本、重建 prompt
或创建替代 Session。
