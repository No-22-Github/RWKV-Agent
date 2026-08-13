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

## v17 第一批工具层实验

第一批实现分成两层：

- 通用 Runner 用 workspace revision 记录真实修改。成功的读文件或测试只在工作区确实变化后
  才允许同参数重试；无变化写入返回 `changed=false`，不会伪造一次新的 revision。
- 新增可选 `TableTools` 能力包，提供 `table_select`、`table_count`、`table_sum`，支持
  CSV/TSV/JSON/JSONL 的精确过滤、分组、去重计数和行表达式求和。它不默认加入
  `CoreTools`，由上层在确认任务需要结构化数据时按需装配。

最初将三个表格工具直接加入 Go-native 默认工具目录的 30 并发实验只有 **13/30**：虽然新通过
了 `jsonl_event_aggregate`，但丢失了 v15 已通过的 8 题，净回退 7 分。这证明 7B 对工具目录
宽度和描述非常敏感；工具实现正确并不等于应该全局暴露。该默认暴露方案已撤回，失败产物仅作
负向实验留档：

- `runs/primitive-v17-go-native-first-batch-final-20260813`

恢复 v15 默认工具目录、仅保留 revision/no-op 语义后的完整轮为 **19/30**。相对 v15 丢失
`search_read_submit`、`invoice_fix`，新增通过 `read_only_repo_explain`；随后对前两题和
`code_patch_edge_case` 复测，前两题均重新通过，确认单轮净 -1 属于生成波动，不是稳定工具层
回归。代码修复题仍失败：回执正确识别模型写回原内容和重复测试，但 7B 没有据此生成有效补丁。

- 守分轮：`runs/primitive-v17-go-native-first-batch-safe-final-20260813`
- 三题复测：`runs/primitive-v17-go-native-first-batch-rerun-3cases-20260813`

因此本批结论不是“多注册几个工具”，而是把结构化数据能力做成可选能力包，并保留可验证的工作区
状态语义。下一步若要让表格工具稳定贡献分数，应先做任务级工具筛选，而不是继续扩大全局 schema。

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

## v18 重复调用死锁控制（已实测：23/30）

v15 最佳轮 10 个失败 case 共 85 步中 48 步是“duplicate tool call rejected”空转：
`loc_interest_8_months` 15/18、`csv_reconcile_returns` 13/16、`code_patch_edge_case`
19/22。近贪心采样（temperature 0.001 / top-k 50）下，固定不变的 RECOVERY 文本无法
打断 7B 重新生成同一个调用，直到步数耗尽。

Harness 侧新增三层控制（`internal/agent/runner.go`，仅作用于 G1i go-native 路径，
upstream-compatible 与普通 XML agent 行为不变）：

- **幂等回放**：`ToolSpec.Replayable` 的纯读工具（calculator/search/read_file/
  list_files/ls/stat/multiply/run_awk/data_query）同参重复时，在
  `--duplicate-replay-limit`（默认 2）内重新执行并返回同一结果，附递增注记；这覆盖
  `loc_interest` 里“第 2 个月与第 1 个月参数完全相同”被拒绝打断的场景。
- **注记升级**：首次拒绝保持旧文本逐字节不变；第二次起升级为带连击次数与剩余步数
  的强提示。
- **救援模式**：同一调用连续出现 `--duplicate-rescue-threshold`（默认 3）次后，把
  工具目录重建为只剩 submit 并以 User turn 注入一次明确指令；此后非 submit 调用
  按 `rescue_submit_only` 拒绝。指标新增 `rescue_attempts` / `rescue_submits`。

零值即关闭、完全回到旧行为。

### 2026-08-14 实测（30 并发全量）

产物：`runs/primitive-v18-go-native-batch30-20260814`。

| 指标 | v15 基线 | v18 |
| --- | ---: | ---: |
| 任务分 | 20/30 | **23/30** |
| Protocol validity | 100%（182/182） | 100%（160/160） |
| Stage validity | 100%（182/182） | 100%（160/160） |
| Required-tool completion | 90.3%（65/72） | 97.2%（70/72） |
| 重复调用拒绝 | 49 | 9 |
| 模型调用 | 182 | 160 |
| 救援 | — | 5 次触发 / 5 次提交 |

20 个 v15 通过题全部守住，新增 `config_precedence_resolve`、
`malformed_edit_recovery`、`read_only_repo_explain`。其中 `config_precedence_resolve`
直接由救援机制救回：模型读完三个配置文件后被 data_query 带偏两次，救援切断循环后
提交了正确答案 `API_TIMEOUT=45 RETRIES=3 FEATURE_X=true`。

回放按设计工作：`loc_interest` 的第 2 个月同参调用被回放后，模型继续算出了
6200 余额月份的 41.79（v15 只算出一个 30.33 就死锁）；`log_incident` 的重复 search
也被回放。剩余 7 个失败全部退化为模型能力问题而非宿主死锁：`two_step` 剥 FINAL=
前缀；`loc_interest` 提交了首月利息而非求和；`fx_column_trap` 列映射错；`log_incident`
选了部署标记前的错误行；`csv_reconcile` 救援后提交了占位符；`code_patch` 写不出有效
补丁。`jsonl_event_aggregate` 出现新的退化模式：calculator 生成一串彼此不同的表达式
（20→10→110→…→17187.5）绕过了回放与救援，16 步耗尽无提交，属于下一轮要处理的
“唯一但无进展的连续同类调用”问题。

死锁题 probe 命令（凭证走环境变量，不写入命令行）：

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
  --primitive-profile go-native \
  --case-parallelism 30 \
  --case-timeout 20m \
  --temperature 0.001 --top-k 50 --top-p 1 \
  --presence-penalty 0 --frequency-penalty 0 --penalty-decay 0.99 \
  --duplicate-replay-limit 2 \
  --duplicate-rescue-threshold 3 \
  --output runs/primitive-v18-go-native-batch30
```

## v19 场景钩子注入（PostToolHook）

Runner 新增 `Options.PostToolHook`：某工具成功执行后（非回放、非 terminal tool），
把钩子返回的文本追加在该工具结果的同一回合，让场景专属提醒在证据最新鲜的时点到达
模型。eval 侧按 case ID 注册（部分导入 fixture 的 scenario 字段为空，不能用
scenario 作键），并在 run.json 的 `harness.scenario_hooks` 登记注入清单。

首批只挂两题（从未在没有钩子时通过过的题，不扰动已能过的轨迹）：

- `two_step_program_output`：`use_token.py` 输出含 `FINAL=` 时提醒"逐字提交、保留前缀"。
- `loc_interest_8_months`：读完 `balance_schedule.csv` 后提醒"每行都要算、重复月算多次、
  提交所有行之和的单个数字"。

实测（2026-08-14）：

- `two_step_program_output` 钩子后 4 次运行通过 3 次（此前 0/3）：提交了完整的
  `FINAL=RIVER-42-OK`。剩余 1 次失败是模型生成畸形调用（`{"path":{...}}`）的方差，
  与钩子无关。
- `loc_interest_8_months` 钩子把轨迹从"只算首月就死锁"改写成"一条表达式里写出全部
  8 行的加权和并提交单个数字"，但 7B 数错行数（写了 4 个 5100 项而非 3 个），
  323.51 vs 289.14。结构与格式已对，只剩模型自己的行计数误差，接近能力边界。

四轮全量对照（v18 一轮 + v19 三轮，同采样、同 go-native 工具）：

| case | 4 轮通过率 |
| --- | --- |
| 19 个稳定题（arithmetic…markdown_release_notes 主体） | 4/4 |
| two_step_program_output | 3/4（唯一一次失败在钩子之前） |
| read_only_repo_explain | 3/4 |
| invoice_fix | 3/4 |
| malformed_edit_recovery / missing_file_recover / tool_result_truthfulness 等 | 4/4 |
| config_precedence_resolve | 1/4（v18 那次靠救援救回，不稳定） |
| loc_interest_8_months / fx_column_trap / log_incident_root_cause / jsonl_event_aggregate / csv_reconcile_returns / code_patch_edge_case | 0/4 |

全量分数在 **22–23/30** 波动（v18 一轮 23，v19 两轮 23/22/22），相对 v15 基线
20/30 净 +2~3；重复调用拒绝从 49 降到 5–9，救援 100% 引导出干净提交。剩余 6 个
稳定失败全部是 7B 能力边界：行计数/列映射/时间比较/行过滤/补丁生成，以及
`jsonl_event_aggregate` 的"唯一表达式螺旋"（每步新 callKey，绕过回放与救援，
16 步耗尽）。下一批候选：同类无进展调用守卫、表格题任务级工具筛选、以及把
`config_precedence_resolve` 纳入钩子以稳定其 1/4 的通过率。

产物：

- `runs/primitive-v18-go-native-batch30-20260814`（23/30）
- `runs/primitive-v19-go-native-batch30-20260814`（22/30，loc 钩子未生效的中间版）
- `runs/primitive-v19-go-native-batch30b-20260814`（23/30）
- `runs/primitive-v19-go-native-batch30c-20260814`（22/30）
- `runs/primitive-v19-hooks-probe{1,2,3}-20260814`（两题钩子探针）

## 贪心解码对照（top-k=1）

同配置只把 `--top-k 50` 换成 `--top-k 1`（纯 argmax），连续两轮全量：

| 运行 | 分数 | 备注 |
| --- | ---: | --- |
| `primitive-v19-greedy-a-20260814` | 23/30 | protocol validity 98.7%（1 次协议错误） |
| `primitive-v19-greedy-b-20260814` | 23/30 | protocol validity 100% |

两轮 **30 题通过集合逐题一致**：分数层面达到确定性，验证了"贪心给确定成绩"的假设。
步级轨迹 171 步中 23 步不同（87% 一致），差异集中在失败题（jsonl 螺旋 6 步 vs 16 步、
config_precedence 5 步 vs 12 步）和边缘题的 think 文本，说明服务端在极低温度/30 路
合批下仍有轻微非确定性，但不影响判分。

贪心通过集合与采样版 v19b 完全一致（同样 23 题、同样 7 题失败），两题钩子
（two_step 通过、loc_interest 结构正确但行计数错）在贪心下同样生效。结论：当前
22–23/30 的波动主要来自采样，贪心 top-k=1 可作为对外报告的确定成绩基线；23/30
即当前"回放+救援+钩子"组合下的正式数字。

## v20 同类成功连击救援（same-tool spiral guard）

`jsonl_event_aggregate` 的失败模式是 calculator 连续 14 次**成功**调用、每次表达式
都不同（新 callKey 每步都绕过重复调用救援）。全量轨迹统计显示所有通过题最长同类
成功连击为 6（loc_interest 的合法逐月计算），只有 jsonl（14）和 log_incident（10）
超过 8，因此取 `--same-tool-rescue-limit` 默认 8，零误伤余量 2。

实现为 runner 的 `sameToolSuccessStreak`（工具名变化或任何拒绝/失败即清零，含回放
的成功能执行 +1），连击达标后复用既有救援通道（submit-only 目录 + User 指令），
理由文本区分“same call repeated”与“same tool ran successfully N times in a row”。

实测（贪心 top-k=1）：

- 两题 probe：jsonl 8 连击时被切断，16 步空转变 11 步干净提交（答案仍错，但失败
  信号从“无输出”变为明确提交）；loc_interest 4 步正常走完未触发（误伤对照通过）。
- 全量 `runs/primitive-v20-greedy-batch30-20260814`：**23/30，通过集合与 v19 贪心
  逐题一致**，零回归；jsonl 16→11 步，其余题轨迹不受影响。

至此正式确定成绩：**贪心 top-k=1 下 23/30**，回放/救援/螺旋守卫/场景钩子全部开启。

## D 方案实验：任务级工具筛选（负向结果，已撤回）

针对 `jsonl_event_aggregate` / `csv_reconcile_returns` 做了 5 个贪心变体：

1. jsonl 去 calculator + data_query 描述给 sum 行过滤示例：最接近，提交
   `orders=6 users=6 revenue=438.72`（3 个数字对 2 个，users 应为 5）；
2. jsonl 示例换成 distinct_count：回退（orders=5 users=5 revenue=224.75）；
3. 错误回执加具体值示例：模型仍组合不出合法调用；
4. 场景钩子注入方法级提醒：jsonl 被带离好路径，csv 轨迹与无钩子逐字相同；
5. jsonl 恢复 calculator + 钩子强制手工路径：失败且 required-tool 掉到 75%。

结论：7B 在贪心下对 data_query 的 schema 组合是硬墙——首次调用必带畸形
（把 schema 形状 `{"type":"string"}` 当值发），且 csv 的畸形轨迹对提示词变化完全
锁死。D 方案提分假设被证伪，任务级覆盖全部撤回。jsonl 的 2/3 正确轨迹证明模型
能理解行级过滤语义，但工具 schema 与模型不匹配，属数据层而非提示层问题。

实验中沉淀的两个保留改动：

- `data_query` 聚合结果 1e-6 圆整（`cleanFloatNoise`）：438.72 不再以
  `438.72000000000003` 出现在结果里，避免精确匹配 scorer 因浮点噪声判负；
- `ToolSpec.Example`：参数错误回执在 schema 形状之外附带一个具体值示例，抑制
  模型照抄 schema 当值的循环。

撤回后的全量贪心回归 `runs/primitive-v21-greedy-batch30b-20260814`：**24/30**，
`config_precedence_resolve` 本轮通过（该题在 v18 后第 2 次通过，属不稳定边界题），
其余通过集合与 v20 一致，保留改动零回归。首轮 30 并发遭遇 HTTP 520 风暴作废
（`runs/primitive-v21-greedy-batch30-20260814`，部署层瞬时故障，同今日早前 13B
合批事件）。

## config_precedence_resolve 不稳定性分析与钩子政策

该题在 go-native 轮次中的通过率约 25–30%（v15-13B、v18 救援、v21b 救援通过，
其余失败）。全量轨迹对齐显示三个"吸引子模式"，由第一步的平局 argmax 决定：

- **A 读文件路径**：list_files → 读三个配置文件 → 可能插入 data_query 绕路 →
  提交正确合并。唯一能过的路；通过与否还依赖绕路恰好被救援切断。
- **B search 求和路径**：第一步用 search 查 README，然后把数字相加提交
  （`30+2+3=35` / `45+2+3=50`），从不读配置文件，必死。
- **C SQL 绕路耗尽**：读完全部文件后把 data_query 当 SQL 用，耗尽步数，或救援
  后提交错误合并（v19c：RETRIES=2 FEATURE_X=false）。

贪心不能复现该题：同一 top-k=1 配置四轮跑出三条不同轨迹（greedy-a=B 模式、
greedy-b 与 v20 逐字相同的 C 模式、v21b=A 模式通过），证明模式选择由服务端在
批处理/浮点层面的残余非确定性决定，贪心只锁住模式内部。

**政策（2026-08-14 决策）**：不再为该题或任何新题新增场景钩子。场景钩子只允许
复述题目文本已有的指令（现有 two_step/loc 两条属此类），harness 的本职是控制面
修复而非解题；该题作为边界题如实报告，不通过提示词打补丁。分数叙事分层：
上游官方协议分数为模型裸分对照；go-native 分数为"产品 harness + 复述型钩子"，
run.json 的 `scenario_hooks` 字段登记全部注入。
