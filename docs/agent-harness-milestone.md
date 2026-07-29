# RWKV-Agent 只读 Agent Harness 里程碑

状态：Phase 1 部分完成

目标：在现有 macOS 本地推理、Conversation 和 State 能力之上，建立可测试、可约束的
Agent step loop；先证明模型能可靠地依据仓库证据回答，再逐步开放有副作用的能力。

## 1. 路线选择

现有推理 CLI、Session 持久化、连续批处理、TUI 和 PTH 直载已经完成真实模型验收。下一个
产品缺口不是新的推理 Demo，而是仓库名称中的 Agent Harness。

第一阶段选择只读仓库 Agent：

1. 第一轮允许普通文本直接回答；只有以 `<tool_call>` 开头的输出进入严格控制帧解析。
2. 工具选择阶段采用 greedy 解码和严格 envelope/JSON 解析。
3. 成功工具调用后切换到独立回答 prompt，使用 G1I `Tool:` role 并预填 `<answer>`；
   文件内容始终视为不可信数据。
4. 限制总 step 和协议重试次数，避免无界循环。
5. 只开放 `list_files`、`read_file`、`search_text`。
6. 暂不开放写文件、shell、Git、网络和动态插件。

## 2. 已落地

- `rwkv-cli agent --model ... --workspace ... --prompt ...` 一次性任务入口。
- `rwkv-cli agent --model ... --workspace ...` 多轮 TUI 入口；交互终端自动选择，
  非交互环境保持 plain 输出。
- Runner 事务化保存进程内 user/assistant/tool transcript；后续轮次的工具选择和独立
  最终回答阶段都携带已提交历史。
- 取消、生成失败、协议错误和 step 超限不提交当前轮；`/new`、`/reset` 显式清空历史。
- Agent TUI 展示 Conversation、step、工具活动、只读权限和工作区，支持当前轮取消后继续。
- `tool` / `final` 两类 G1I envelope 动作及严格字段校验。
- 普通文本 final 与 G1I 工具控制帧的联合输出语义。
- 一次协议纠错重试和 1–20 step 硬上限。
- 工作区相对路径、`..`、绝对路径和符号链接越界检查。
- 64 KiB 单文件上限、2 MiB 搜索文件上限和结果数量上限。
- 工具调用、工具结果和独立最终回答阶段的消息闭环。
- 模型无关的 completion 注入；控制提示支持标准 system 与 G1 inline 两种装配模式。
- 独立的 `continuation.Generator`、`ActionProtocol` 和 `PromptRenderer` 接口。
- 本地 inference Session 续写 adapter。
- `rwkv_lightning` 非流式 HTTP 续写 adapter；endpoint 可配置，密码来自环境变量。
- `rwkv-g1i-envelope-v1` 与 `rwkv-chat-continuation-v1` 独立版本标识。
- 协议、循环、路径越界、截断、搜索与读取的无模型单元测试。
- 回答阶段对长字符串保留开头和任务相关窗口，单个字符串约束为 2400 Unicode 字符。

2026-07-30 的 `rwkv-g1i-13b-4922` 远程 smoke test 覆盖直接回答、`read_file` 和
`search_text`，三条均完成且未触发协议重试。旧裸 JSON 协议已经删除。协议结构参考
`123123213weqw/rwkv-agent`；完整能力评测计划复用 `marty1885/primitive-bench`。
“你有哪些工具”和包含协议标签的文档总结也已回归通过。

## 3. 当前边界

- Agent transcript 已支持进程内多轮提交和重置，但尚未接入不可变 Session bundle，
  进程退出后不能续跑。
- 尚无全局 token 预算；当前只有回答阶段的单字符串字符预算。
- 没有结构化输出约束，当前依赖 prompt、严格解析和一次纠错。
- 还没有覆盖中英文任务、错误工具参数和多步查找的真实模型成功率基准。
- 当前只验证了 13B 的直接回答与单工具链路，7B/3B 尚未形成可比较数据。
- 当前 1.5B G1 的协议遵循不足，不能把 CLI 入口视为可用 Agent 产品。
- 任务相关性压缩是轻量词项窗口选择，尚未做 tokenizer 级预算或语义重排。
- 不支持并行工具调用。
- 一个工具成功后固定进入回答阶段，尚不支持需要多个成功工具调用的任务。
- `rwkv_lightning` 当前只返回通用 `finish_reason=stop`，预算耗尽与命中 stop string
  无法可靠区分；CLI 暂以 256 token 限制工具选择，以 1024 token 默认回答预算降低
  语义截断概率。
- 远程续写第一版还没有 SSE 流式输出、usage 统计或服务端 State 对接。

## 4. 下一步 Checklist

### Commit A：Agent Session 持久化

- transcript 保存 system/user/assistant/tool 的完整结构化消息。
- Agent revision 绑定工具注册表版本与工作区标识。
- 中断后只恢复已完成 step，不保存半个模型动作或半个工具结果。
- native State 不可用时从 transcript replay。

### Commit B：上下文预算

- 每步生成前统计 prompt token。
- 工具结果按字节和 token 双重限制。
- 超预算时先丢弃可重新获取的旧工具正文，保留路径、摘要和 checksum。
- 明确报告压缩次数、压缩前后 token 和是否触发 replay。

### Commit C：权限契约

- 为 ToolSpec 增加只读、写入、命令和网络权限分类。
- 定义确认请求、拒绝、超时和取消事件，但暂不注册有副作用的工具。
- 权限判定由宿主执行，不能依赖模型输出或控制 prompt。
- 为工作区外访问、符号链接替换和隐藏路径建立统一策略。

### Commit D：适配更强模型与协议评测

- 适配 `primitive-bench` 的 30 个文件型任务、隔离工具环境和评分规则。
- 覆盖直接回答、单工具、多工具、错误参数和越权请求。
- 输出动作合法率、任务完成率、平均 step、重试率、token 和耗时。
- 达不到预设门槛时保持实验性入口，不开放有副作用工具。

### Commit E：可写工具与扩展

- 协议评测稳定后先增加结构化 patch 工具，不直接开放任意 shell。
- 所有写操作展示精确目标和 diff，获得用户确认后执行。
- 写入后运行选定的只读验证命令；验证命令与写权限分开授权。
- 工具声明包含权限、超时、输出上限和可取消语义。
- 网络与外部插件保持显式启用，不作为本地 Agent 默认能力。

## 5. 完成定义

只读 Agent 里程碑只有在以下条件全部满足后才能标记完成：

1. 固定真实模型评测达到动作合法率和任务完成率门槛。
2. 多步任务可保存、退出、恢复，并保持 transcript/State revision 一致。
3. 取消、协议错误、工具错误和 step 超限均不留下伪完成记录。
4. 长任务有明确上下文预算和可观测的压缩行为。
5. `go test ./...`、`go test -race ./...` 与真实模型 Agent smoke test 通过。

在此之前，项目状态应保持“Phase 1 部分完成”。
