# Primitive Bench v12 基线（2026-08-13）

## 范围

- 数据集：`RWKV-Vibe/rwkv-Primitive-Bench/agent_cases_orig30`，共 30 题。
- 上游快照：`416b073d2c5442ae34bfbf8a3b84ed414b5b85ff`。
- RWKV-Agent：`c94a35b`，Harness `rwkv-agent-eval-v12`。
- 模型：`rwkv7-g1i-7.2b-20260805-ctx16384`。
- 接口：`rwkv_lightning_cuda /v1/batch/completions`。
- 每题使用上游原始 `max_turns`（6–22），case 间目前串行，case 内工具调用串行。

## 结果

全量原始结果为 **12/30（40.0%）**。其中 `find_read_submit` 因单次 HTTP 请求
`unexpected EOF` 失败；相同配置单题补跑为 1/1 通过。替换这一项后的当前有效基线为
**13/30（43.3%）**。这不是一次完全无网络错误的整轮结果，后续对外发布时应再跑一轮确认。

| 指标 | 结果 |
| --- | ---: |
| Protocol validity | 93.6%（219/234） |
| Required-tool completion | 72.2%（52/72） |
| Forbidden-tool avoidance | 100%（2/2） |
| 重复工具调用拒绝 | 101 次 |

排除网络失败后，17 个失败由 9 个步数耗尽、6 个工具调用协议错误，以及 2 个评分条件未满足组成。目前最明显的问题是模型重复调用已经成功或已经失败的工具，导致无法进入 `submit`；其次是长 JSON 工具调用出现截断或非法换行。

旧 v11 的 14/30 使用统一 `--max-steps 12`，会截断原始预算为 16、18、22 的案例，不应作为正式对外分数与 v12 直接比较。

## 复跑

凭证只通过环境变量传入，不写入命令、代码或评测产物：

```sh
export RWKV_CF_ACCESS_CLIENT_ID='...'
export RWKV_CF_ACCESS_CLIENT_SECRET='...'

go run ./cmd/rwkv-cli agent-eval \
  --completion rwkv-lightning \
  --api-url https://api-125-7b.rwkvos.com/v1/batch/completions \
  --api-header-env CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID \
  --api-header-env CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET \
  --api-stop-tokens cuda \
  --api-stream=true \
  --model rwkv7-g1i-7.2b-20260805-ctx16384 \
  --suite primitive \
  --case-timeout 8m \
  --temperature 0.1 --top-k 1 --top-p 1 \
  --presence-penalty 0 --frequency-penalty 0 --penalty-decay 1 \
  --output runs/primitive-v12
```

本次本地产物位于：

- `/tmp/rwkv-agent-primitive-full-v12-20260813-16`
- `/tmp/rwkv-agent-primitive-v12-rerun-find-20260813-17`

## Native G1i 协议分支试验

分支 `codex/primitive-native-g1i` 吸收了上游 G1i continuation 协议和运行方式：

- `System: Tools:` 扁平工具目录、`Assistant: ```json` 预填充，以及
  `User: Function output:` 工具结果回合；
- `submit` 成功后立即结束，不再要求模型额外生成一次 plain-text final；
- 容忍字符串化 `arguments`、原始控制字符、截断 JSON、非法转义、无名调用、
  `arguments`/`args`/`parameters` 字段别名，以及单调用的 OpenAI `<tool_calls>` 包装；
- G1i 回合不注入通用 Agent reminder；重复调用与上游一致，继续执行并附 NOTE；
- 30 个 case 并发，并在 10ms 窗口内合并为一个 `contents[]` 请求，再按
  `choices[].index` 拆分结果；
- 对齐上游 CUDA stop token 和采样参数：temperature 0.001、top-k 50、top-p 1、
  alpha decay 0.99。

首个 30 并发实现错误地发送了 30 个独立 HTTP 请求，产生大量 524，2/30 的结果已作废。
改为官方式合批后，三次结果如下：

| 运行 | 通过 | Protocol validity | Required-tool completion | 备注 |
| --- | ---: | ---: | ---: | --- |
| 合批首轮 | 19/30 | 100.0% | 93.1% | 8m case deadline 截断 4 题，只作为下界 |
| 无超时复跑（追加 wrapper/repeat 修复前） | 16/30 | 98.9% | 95.8% | 无网络错误 |
| 最终代码 | **17/30** | **97.7%** | **88.9%** | 无网络错误或超时 |
| 上游官方留档 | **20/30** | — | — | 同模型单次运行 |

最终代码相对有效 v12 基线从 13/30 提升到 17/30。三轮 pass 集合有明显波动，说明单次
30 题结果的方差不小；协议收益更稳定地体现在 validity、工具完成率，以及字符串化参数等
原先直接丢失的调用被成功执行。最终轮中 arithmetic 的 OpenAI `<tool_calls>` 输出已被正确
解析并通过。

剩余失败已主要从协议失败转为执行质量失败：表格/JSONL 聚合算错、Lua 程序过长或使用错误
的数据访问方式、漏掉输出固定前缀，以及失败后重复同一策略直到步数耗尽。下一批最值得继续
吸收的是上游的参数别名/宽容参数归一化和 Primitive 工具环境细节；这两项应与模型能力优化
分开评测，避免把 harness 行为差异算到模型上。

最终产物：

- `runs/primitive-v13-native-g1i-final-batch30-20260813`
- `runs/primitive-v13-native-g1i-batch30-20m-20260813`
- `runs/primitive-v13-native-g1i-batch30-20260813`

## v14 Go 原生工具双轨

Harness v14 新增显式 `--primitive-profile`：默认 `upstream-compatible` 继续作为官方协议
对照；`go-native` 使用完全相同的 30 题、fixture、逐题 `max_turns` 和 scorer，只在题目原本
提供 `run_lua` 时将其替换为 RWKV-Agent 的 Go 原生核心工具：

- `calculator`：受限算术、`abs/min/max/round`、可选 0–15 位定点结果；
- `data_query`：CSV/TSV/JSON/JSONL 精确过滤、字段选择、分组，以及
  `count/sum/avg/min/max/distinct_count`；每次调用执行一个聚合，数值聚合可使用
  `qty*unit_price` 一类安全行表达式。

普通 `agent` 命令也注册同一套核心工具。这样 Go-native 分数直接反映产品工具栈，Lua 兼容
能力不再成为产品门槛，同时保留 upstream-compatible 分数用于和官方 Harness 做协议诊断。

### 2026-08-13 实测状态

- 首个无网络错误的 Go-native 原型整轮为 **17/30**，protocol validity 100%，与 v13
  upstream-compatible 最终轮同分。trace 证明模型会发现新工具，但最初的嵌套多聚合 schema
  容易被 7B 模型当作参数内容照抄。
- 最终接口因此收敛为一次一个扁平操作：`operation` + `field` 或 `expression`；最终二进制的
  `csv_sum` sanity 为 **1/1**，轨迹是 `read_file -> calculator -> submit`。
- 最终代码的两次 30 并发全量尝试均因部署层 524 作废：第一次 23 个 case 报 HTTP 524，
  第二次 30/30 都在首个模型调用报 HTTP 524，protocol 分母为 0。它们分别保存在
  `runs/primitive-v14-go-native-final-batch30-20260813` 和
  `runs/primitive-v14-go-native-final-batch30-retry-20260813`，不能当作模型或 Agent 分数。
- 服务恢复后的最终无网络错误整轮为 **20/30**，protocol validity **98.9%**（182/184）、
  required-tool completion **91.7%**（66/72）、forbidden-tool avoidance **100%**（2/2）。
  产物位于 `runs/primitive-v14-go-native-final-healthy-batch30-20260813`。

因此当前正式 Go-native 成绩为 **20/30**，与同模型上游官方留档 **20/30** 持平；已经达到
“使用 Go 原生通用工具栈时不低于官方 Lua 框架”的本轮目标。

## v15 通用 Agent 控制面加固

Harness v15 不再改变 Primitive 题库或 Go 原生工具语义，集中修复可以回收到产品框架的控制面
问题：

- answer 阶段硬拒绝任何工具调用，包括藏在 final 文本里的 bare JSON 或 `<tool_call>`；新增
  stage contract 指标和 answer-stage tool-call 计数；
- 将“保持上游工具顺序”和“允许重复执行”拆成两个独立策略。`upstream-compatible` 仍完整保留
  上游行为，`go-native` 则拒绝同参数重复调用，并把恢复指令放进同一个 Function output 回合；
- 普通 `agent` 只暴露工作区工具和本地 `calculator`、`data_query`、`datetime`，不再把固定 mock
  天气、交通、汇率伪装成产品能力；这些 provider-backed 工具仅留在可重复的 assistant eval；
- G1I 计算提示明确区分 calculator 的纯数值表达式和 data_query 的表格操作，减少把文件名、SQL
  或自然语言误传给计算器的情况。

同模型、同 30 题、30 并发回归仍为 **20/30**，protocol validity 从 v14 的 **98.9%** 提升到
**100%（182/182）**，stage contract validity **100%（182/182）**，answer-stage tool calls 为
**0**；required-tool completion 为 **90.3%（65/72）**。任务分没有回退，剩余 10 题仍集中在
多步计算/表格聚合、固定输出前缀遗漏、失败后策略循环和代码修复收敛，而不是协议解析。

Toolcall-Bench 的 280 样本格式探测也支持继续使用当前 G1I 主路径：7.2B 的裸提示格式先验不
可靠，宿主应显式预填 `Assistant: ```json`、在 closing fence 截停，并注入
`User: Function output:`。因此 v15 没有为了题库引入 Lua，也没有切换到另一套工具标签协议。

本轮回归产物：

- `runs/primitive-v15-go-native-final-healthy-batch30-20260813`

### 13.3B 追加对照

同日使用 `rwkv7-g1i-13.3b-20260805-ctx16384` 和相同 Harness v15、Go-native profile、
题库、采样参数及逐题 step budget 做了追加测试。13B 端点在一次合并 30 条 contents 时对全部
请求返回 `HTTP 400: Invalid JSON`；单题探针可正常生成，因此该 0/30 是 batch 宽度不兼容，
不是有效模型成绩。将 case parallelism 降到 10 后完成了无传输错误的 30 题全量轮。

| 模型 | 并发/最大 batch | 通过 | Protocol validity | Stage validity | Required tools | 重复调用拒绝 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| G1I 7.2B | 30 | **20/30** | 100.0%（182/182） | 100.0%（182/182） | 90.3%（65/72） | 49 |
| G1I 13.3B | 10 | **15/30** | 99.1%（214/216） | 100.0%（214/214） | 86.1%（62/72） | 84 |

13.3B 的有效工具执行数与 7.2B 接近（130 vs 132），但总模型调用更多（216 vs 182）、重复
调用拒绝明显更多（84 vs 49），说明主要退化来自工具策略循环，而不是 JSON 格式能力。13B
没有发生协议自动修复，7.2B 有 17 次修复；模型规模在这个 Agent harness 上并不呈单调收益。
13B 的 15 个失败由 7 个 step-limit、7 个 scorer 未满足和 1 个 arithmetic 结果轮空响应组成。

两者通过集合也不完全相同：13B 额外通过了 `config_precedence_resolve`、
`loc_interest_8_months`、`two_step_program_output`，但丢失了 7.2B 已通过的 8 题。这进一步表明
后续优化应优先处理循环恢复和任务状态推进，而不是继续堆叠格式提示。

13.3B 有效产物：

- `runs/primitive-v15-go-native-13b-batch10-20260813`

30-wide batch 诊断产物（无效成绩，仅保留服务兼容性证据）：

- `runs/primitive-v15-go-native-13b-final-healthy-batch30-20260813`

```sh
go run ./cmd/rwkv-cli agent-eval \
  --completion rwkv-lightning \
  --api-url https://api-125-7b.rwkvos.com/v1/batch/completions \
  --api-header-env CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID \
  --api-header-env CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET \
  --api-stop-tokens cuda \
  --model rwkv7-g1i-7.2b-20260805-ctx16384 \
  --suite primitive \
  --primitive-profile go-native \
  --case-parallelism 30 \
  --case-timeout 20m \
  --output runs/primitive-v14-go-native
```
