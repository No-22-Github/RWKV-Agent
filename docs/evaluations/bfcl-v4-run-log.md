# BFCL v4 跑分日志

本文件是 BFCL v4 A+B 的长期、只追加运行记录。每次完成官方判分后新增一条，不覆盖历史结果；`runs/bfcl/` 保存可再生成的详细产物，本文件保存应进入 Git 的索引、结论和比较边界。

## 记录规则

- 只把经过固定版本官方 evaluator 判分的完整运行列入“正式评分”。
- 单题探针、子集冒烟、负向验收、中断运行和确定性复跑列入“辅助运行”，不作为正式模型分数。
- 每条正式评分必须记录数据 commit、evaluator 版本、模型、档位、transport、题量、并发、采样、成功/失败/跳过、解析失败、耗时和产物路径。
- 不同“比较组”的数字不可直接比较。同组数字仍须结合该组注明的协议边界解释。
- 分数均来自官方 evaluator；Go 侧只生成结果，不实现或预判评分逻辑。

## 固定环境

- 数据集：BFCL v4，commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`
- evaluator：`bfcl-eval==2026.3.23`
- 本地 decode-only 注册名：`rwkv-agent-bfcl-ab-v1`
- 正式分数文件：`score/<model>/.../*_score.json`

## 可比性分组

| 比较组 | 共同条件 | 可解释为 | 不可解释为 |
|---|---|---|---|
| `M1-native-fc` | 同一原生 Chat Completions tools 路径、官方 evaluator | 适配器健康度或同协议原生 FC 对比 | 与 Markdown baseline 的直接能力差 |
| `M1-official-control` | 官方 `QwenFCHandler`、手工 tool prompt、`/v1/completions` | 本地模型服务与公开 Qwen3-8B FC 分数的复现程度 | RWKV-Agent 原生适配器本身的成绩 |
| `M2-markdown-single-call` | 同一 400 题、同一 Markdown prompt renderer、严格 parser、每题一次调用、官方 evaluator | 相同 Harness 和输出契约下的“模型 + transport/template”系统差异 | 纯模型权重差异或字节级完全同协议差异 |
| `M2.5-parser-calibration` | 完全复用 RWKV M2 原始 trace,仅切换 parser mode | wire-format compat 对既有输出的可恢复增量 | 新一次模型成绩、生成策略收益或公平矩阵格 |
| `E1-E2-anchor-v1-v2` | v2 固定 491 题、`bfcl-markdown-anchor-v1`、首轮 prompt hash 相同、并发 8、官方 partial evaluator | 同一服务内 baseline/enhanced 的实测系统差异 | 官方全榜 Overall；有输出漂移时也不可把 E1/E2 全部 delta 归因于 Harness |
| `E3-finish-task-probe` | 全量 1124 个负样本、额外注入 `finish_task`、strict parser、官方 partial evaluator | 模型是否愿意显式选择 stop tool，以及拦截后的弃权成绩 | E1/E2 矩阵分数；该探针改变了工具表和提示协议 |
| `E7-multi-turn-single-case` | `multi_turn_base_0`、持久 sidecar、官方 partial evaluator | 多轮 Harness 与 Agent 循环是否闭环、干预事件和单题失败归因 | 模型多轮总体能力或 E8 正式矩阵成绩 |
| `validation-only` | 固定 evaluator 与人工构造结果 | 数据、目录、decoder 和错误分支是否闭环 | 模型能力 |

`M2-markdown-single-call` 中，RWKV 直接接收 continuation prompt；Chat Completions 模型还会经过 wrapped system instruction 和服务端 chat template，并受最多 4 个 stop sequence 的接口限制，而 RWKV M2 使用 5 个。因此该组具有强诊断可比性，但不是 transport/template 完全一致的模型级隔离实验。

## 正式评分总表

| 日期 | Run | 比较组 | 模型 | Split | 正确/总数 | 准确率 | 并发 | 解析失败 | 耗时 |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| 2026-08-21 | `e3-rwkv7b-finish-task-c8-full-20260821` | `E3-finish-task-probe` | RWKV7 G1i 7.2B | `irrelevance` | 75/240 | 31.25% | 8 | 0 | 614.63s 两 split 合计 |
| 2026-08-21 | `e3-rwkv7b-finish-task-c8-full-20260821` | `E3-finish-task-probe` | RWKV7 G1i 7.2B | `live_irrelevance` | 355/884 | 40.16% | 8 | 0 | 614.63s 两 split 合计 |
| 2026-08-21 | `e3-qwen8b-finish-task-c8-full-20260821` | `E3-finish-task-probe` | Qwen3-8B-FP8 | `irrelevance` | 184/240 | 76.67% | 8 | 0 | 196.11s 两 split 合计 |
| 2026-08-21 | `e3-qwen8b-finish-task-c8-full-20260821` | `E3-finish-task-probe` | Qwen3-8B-FP8 | `live_irrelevance` | 461/884 | 52.15% | 8 | 0 | 196.11s 两 split 合计 |
| 2026-08-21 | `e2-rwkv7b-enhanced-anchor2-c8-v2-20260821` | `E1-E2-anchor-v1-v2` | RWKV7 G1i 7.2B | A+B v2 13 splits | 267/491 | 54.38% | 8 | 7 | 450.29s |
| 2026-08-21 | `e1-rwkv7b-baseline-anchor2-c8-v2-20260821` | `E1-E2-anchor-v1-v2` | RWKV7 G1i 7.2B | A+B v2 13 splits | 266/491 | 54.18% | 8 | 6 | 327.41s |
| 2026-08-21 | `e2-qwen8b-enhanced-anchor2-c8-v2-20260821` | `E1-E2-anchor-v1-v2` | Qwen3-8B-FP8 | A+B v2 13 splits | 315/491 | 64.15% | 8 | 23 | 141.89s |
| 2026-08-21 | `e1-qwen8b-baseline-anchor2-c8-v2-20260821` | `E1-E2-anchor-v1-v2` | Qwen3-8B-FP8 | A+B v2 13 splits | 313/491 | 63.75% | 8 | 23 | 161.89s |
| 2026-08-19 | `qwen-markdown-baseline-full-c16-t001-20260819` | `M3-baseline-full-diagnostic` | Qwen3-8B-FP8 | A+B 13 splits | 正样本 2064/2517;负样本 115/1124 | 82.00%;10.23% | 16 | 56 | 603.35s |
| 2026-08-18 | `m2.5-rwkv-wire-compat-v1-20260818` | `M2.5-parser-calibration` | RWKV7 G1i 7.2B | `simple_python` | 365/400 | 91.25% | 复用源运行 64 | 4 | 离线重解析 0.007s |
| 2026-08-18 | `qwen-markdown-baseline-simple-python-400-c16-20260818` | `M2-markdown-single-call` | Qwen3-8B-FP8 | `simple_python` | 386/400 | 96.50% | 16 | 0 | 45.48s |
| 2026-08-18 | `m2-smoke-20260818` | `M2-markdown-single-call` | RWKV7 G1i 7.2B | `simple_python` | 115/400 | 28.75% | 64 | 275 | 132.19s |
| 2026-08-18 | `m1-qwen3-8b-fp8-fixed-20260818` | `M1-native-fc` | Qwen3-8B-FP8 | `simple_python` | 376/400 | 94.00% | 8 | 0 | 1202.01s 三个 split 合计 |
| 2026-08-18 | `m1-qwen3-8b-fp8-fixed-20260818` | `M1-native-fc` | Qwen3-8B-FP8 | `multiple` | 188/200 | 94.00% | 8 | 0 | 1202.01s 三个 split 合计 |
| 2026-08-18 | `m1-qwen3-8b-fp8-fixed-20260818` | `M1-native-fc` | Qwen3-8B-FP8 | `live_simple` | 210/258 | 81.40% | 8 | 0 | 1202.01s 三个 split 合计 |
| 2026-08-18 | `m1-official-handler-20260818` | `M1-official-control` | Qwen3-8B-FP8 | `simple_python` | 381/400 | 95.25% | 8 | N/A | 1402s 三个 split 合计 |
| 2026-08-18 | `m1-official-handler-20260818` | `M1-official-control` | Qwen3-8B-FP8 | `multiple` | 191/200 | 95.50% | 8 | N/A | 1402s 三个 split 合计 |
| 2026-08-18 | `m1-official-handler-20260818` | `M1-official-control` | Qwen3-8B-FP8 | `live_simple` | 217/258 | 84.11% | 8 | N/A | 1402s 三个 split 合计 |

## 2026-08-21 — E4–E7 multi-turn 前置门禁与单题闭环

- E4 固定了 `bfcl-eval==2026.3.23` 的多轮执行、holdout、公开状态比较和 20-step 语义；确认 `STATELESS_CLASSES=["MathAPI"]`，并纠正数据实际包含单轮 case 的假设。
- E5 使用仓库固定 RWKV World tokenizer 实际编码全部 800 题完整 prompt：`ctx16384` 扣除每步 1024 max output 后，prompt 预算为 15360 token；全量 catalog 与理想 class 收窄均可行 758/800，共同可行集 758/800；42 个不可行 case 全部来自 `long_context`。此前所有字符/token 比例估算均由本结果取代。
- E6 sidecar GT 门禁：`multi_turn_base` 官方 200/200；额外 `mkdir` 负向样本 0/1，命中 `multi_turn:instance_state_mismatch`。
- E7 为辅助运行，不进正式评分总表。Qwen baseline/enhanced、RWKV baseline/enhanced 在 `multi_turn_base_0` 上均完成结果落盘和官方 evaluator，成绩均为 0/1；失败类型依次为 `empty_turn_model_response`、`instance_state_mismatch`、`empty_turn_model_response`、`force_terminated`。
- E7 证明了结果形状、持久执行、工具结果回喂、事件 trace 与官方判分闭环；它不证明模型答对，亦不可外推总体多轮能力。

详细实现、上下文分布和四组 trace 归因：`docs/evaluations/bfcl-v4-multi-turn-e4-e7-20260821.md`。

## 2026-08-21 — E3 finish_task 全量弃权探针

### 协议与运行冻结项

- Renderer：`bfcl-markdown-finish-task-v1`。在题目原工具表尾部注入无参数控制工具 `finish_task`，描述为“没有任何任务工具适用时结束任务”；单调用 prefill 仍为 `{"name":"`。
- Harness 分层：trace 的 `tool_calls` 保留模型原始调用并记录 `probe_selection=finish_task|real_tool|no_call|mixed`；只有纯 `finish_task` 被拦截为空 result。真实工具和混合调用仍写入 result，不能借控制工具掩盖错误调用。
- 数据：BFCL v4 commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`，全量 `irrelevance` 240 + `live_irrelevance` 884，共 1124 题；evaluator `bfcl-eval==2026.3.23`，带 `--partial-eval`。
- Harness 二进制 SHA-256：`ea7984073dd8df2db4c2beebf91d0cfd587585da7aad1969f391ac7afdf5eacf`；源码基点 `b33acbf0d92d550eaa07e834ccbef5719a725e47`，运行时工作树 dirty，精确实现由 binary hash、`run.json` 与 trace 固化。
- RWKV：`rwkv7-g1i-7.2b-20260805-ctx16384`，云端 `rwkv_lightning` continuation + SSE + text stop，temperature `0.001`、`concurrency=8`、`remote-batch-wait=50ms`。
- Qwen：端点注册名 `Qwen/Qwen3-8B-FP8`，本地 vLLM wrapped continuation，thinking disabled、temperature `0`、`concurrency=8`。用户把本地服务描述为 int8，但本轮只确认了服务注册名，未独立核实实际量化格式。

### 模型层选择与判分层结果

| 模型 | Split | `finish_task` | 自然 no-call | 真实工具 | 官方空调用成绩 |
|---|---|---:|---:|---:|---:|
| RWKV7 G1i 7.2B | `irrelevance` 240 | 73（30.42%） | 1（0.42%） | 166（69.17%） | 75/240（31.25%） |
| RWKV7 G1i 7.2B | `live_irrelevance` 884 | 336（38.01%） | 19（2.15%） | 529（59.84%） | 355/884（40.16%） |
| Qwen3-8B-FP8 | `irrelevance` 240 | 180（75.00%） | 4（1.67%） | 56（23.33%） | 184/240（76.67%） |
| Qwen3-8B-FP8 | `live_irrelevance` 884 | 439（49.66%） | 22（2.49%） | 423（47.85%） | 461/884（52.15%） |

- RWKV 总体选择：`finish_task` 409/1124（36.39%），自然 no-call 20/1124（1.78%），真实工具 695/1124（61.83%）。Qwen 分别为 619/1124（55.07%）、26/1124（2.31%）、479/1124（42.62%）。两轮基础设施失败/跳过均为 0/0。
- RWKV `irrelevance` 的官方正确数比 `finish_task + no_call` 多 1：`irrelevance_233` 的真实调用含 Python 关键字参数 `from`，官方 AST decoder 不能解码，按负样本规则判为成功弃权。这是 evaluator 语法口径，不是模型选择了 stop tool；模型层计数以 trace 为准。
- 结论：显式 stop tool 对两模型都提供了工程增益，但未解决 g1i 的弃权缺陷；RWKV 仍在 61.83% 的全量负样本上选择真实工具。该运行改变工具表与提示协议，只能作为独立 E3 证据，不能并入 E1/E2 baseline/enhanced delta。

正式产物：

- RWKV：`runs/bfcl/e3-rwkv7b-finish-task-c8-full-20260821`
- Qwen：`runs/bfcl/e3-qwen8b-finish-task-c8-full-20260821`
- 两目录均含 `run.json`、`summary.json`、`trace.jsonl`、`result/` 和官方 `score/`。

## 2026-08-21 — E0/E1/E2 anchor-v1 + v2 491 题

### 运行冻结项与评分口径

- 数据：BFCL v4 commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`；manifest `configs/bfcl-sample-v2.json`，SHA-256 `f691e923da092230ca1d6692168fbaabc5425883c29814e9ce028161842b7914`。
- evaluator：`bfcl-eval==2026.3.23`，命令带 `--partial-eval`；因此下表是 491 个实际条目的官方 split 分数和加权值，不使用 evaluator 将未跑 multi-turn 等大类按 0 纳入的 `Overall Acc`。
- Harness 二进制 SHA-256：RWKV E1/E2 与 Qwen E1 为 `c7499db6817283756ce0524d082f8103e678bc9069f222bdd01ce82a2a1bb068`；Qwen E2 在修复 wrapped self-contained retry transcript 后为 `f8e58dc7c103fbd4f8b629a25cad219b4ddac6325e2bbd5daf790e539cdab933`。源码基点均为 `1cb107ae280801647a2fd16c3dd395058afab230`，运行时工作树为 dirty；精确实现由 binary hash、`run.json` 与 trace 固化。修复不改变首轮 renderer 或 parser，只改变首次解析失败后的纠错 transcript。
- Renderer：两档均为 `bfcl-markdown-anchor-v1`，单调用预填 `{"name":"`，并行预填 `[{"name":"`。两模型 E1/E2 的 491 个首轮 `prompt_sha256` 均逐题相同。
- Baseline：strict、一次模型调用。Enhanced：strict 失败后尝试 wire-compat；仍失败才用固定纠错 prompt retry 一次。负样本的 strict 解析失败视为 no-call，不 retry。
- RWKV：`rwkv7-g1i-7.2b-20260805-ctx16384`，`rwkv_lightning` Python，continuation + SSE + text stop，temperature `0.001`，`concurrency=8`，`remote-batch-wait=50ms`。
- Qwen：`Qwen/Qwen3-8B-FP8`，本地 vLLM，wrapped continuation，thinking disabled，temperature `0`，`concurrency=8`。已知 FP8/batching 有固定底噪；并发用于缩短运行时间，不把跨运行输出漂移解释成并发因果。

### E0 确定性门禁

| 模型/配置 | A/B 生成 | 字节一致 | 耗时 A/B | 结论 |
|---|---:|---:|---:|---|
| RWKV c1，batch wait 0 | 各 20/20，失败/解析失败/跳过均 0 | 20/20 | 45.87s / 46.86s | 通过 |
| RWKV c8，batch wait 50ms | 各 20/20，失败/解析失败/跳过均 0 | 20/20 | 14.37s / 14.63s | 通过；作为正式 E1/E2 配置 |
| Qwen c1 | 各 20/20，失败/跳过 0，解析失败各 1 | 20/20 | 29.72s / 29.42s | 串行控制通过 |
| Qwen c8 | 各 20/20，失败/跳过 0，解析失败各 1 | 19/20 | 5.14s / 5.18s | `live_relevance_0-0-0` 的图片尺寸参数漂移；结合 2026-08-20 诊断，作为已知 FP8/batching 底噪接受并发运行 |

RWKV 对比报告：`runs/bfcl/e0-rwkv7b-anchor2-c1-determinism-20260821.json`、`runs/bfcl/e0-rwkv7b-anchor2-c8-batch50-determinism-20260821.json`。Qwen 对比报告：`runs/bfcl/e0-qwen8b-anchor2-c1-determinism-20260821.json`、`runs/bfcl/e0-qwen8b-anchor2-c8-determinism-20260821.json`。更早的 `e0-qwen8b-anchor-c8-a-20260821` 是 anchor 组装修正前的无效实现诊断，不进入任何评分。

### E1/E2 官方分项

| Split | 题数 | RWKV E1 | RWKV E2 | Qwen E1 | Qwen E2 |
|---|---:|---:|---:|---:|---:|
| `simple_python` | 40 | 87.50% | 87.50% | 92.50% | 92.50% |
| `simple_java` | 100 | 37.00% | 37.00% | 54.00% | 52.00% |
| `simple_javascript` | 15 | 53.33% | 53.33% | 60.00% | 66.67% |
| `multiple` | 30 | 96.67% | 96.67% | 96.67% | 96.67% |
| `parallel` | 30 | 86.67% | 86.67% | 76.67% | 76.67% |
| `parallel_multiple` | 30 | 73.33% | 76.67% | 83.33% | 83.33% |
| `irrelevance` | 30 | 0.00% | 0.00% | 10.00% | 10.00% |
| `live_simple` | 60 | 73.33% | 73.33% | 75.00% | 76.67% |
| `live_multiple` | 40 | 72.50% | 72.50% | 87.50% | 87.50% |
| `live_parallel` | 16 | 75.00% | 75.00% | 62.50% | 62.50% |
| `live_parallel_multiple` | 24 | 37.50% | 37.50% | 70.83% | 79.17% |
| `live_relevance` | 16 | 93.75% | 93.75% | 100.00% | 100.00% |
| `live_irrelevance` | 60 | 0.00% | 0.00% | 16.67% | 16.67% |
| **491 题加权** | **491** | **266/491，54.18%** | **267/491，54.38%** | **313/491，63.75%** | **315/491，64.15%** |

### Enhanced 归因与边界

- RWKV E2：retry 7 题，retry 后可解析 0；wire-compat 直接修复 0。E1/E2 首次生成 487/491 相同，4 个输出漂移 ID 为 `parallel_multiple_89`、`live_parallel_multiple_3-2-1`、`live_relevance_1-1-0`、`live_irrelevance_347-81-8`。表面 +1 题来自跨运行输出变化，不是 retry 救回，不能归因于 Harness。
- Qwen E2：retry 25 题，retry 后可解析 3（`simple_java_36`、`live_simple_107-64-0`、`live_parallel_multiple_23-20-0`）；wire-compat 直接修复 0。E1/E2 首次生成 445/491 相同，最终 BFCL result 451/491 相同。官方加权表面 +2 题，但分项同时有升有降，FP8/batching 漂移与 retry 收益混合，不能把 +0.41 pp 全部当作确定的 Harness 增益。
- 两模型 E1/E2 的失败/跳过均为 0/0。RWKV E1/E2 strict 最终解析失败为 6/7；Qwen 为 23/23。负样本低分是模型没有弃权，不是 evaluator 或生成基础设施失败。
- 结论：本轮最可靠的 E2 证据是“机制触发与恢复清单”，不是一次 A/B 分差。若要隔离纯 Harness delta，应冻结同一份首轮输出做离线 parser/retry 模拟，或对 E1/E2 做多轮配对复跑。

正式产物：

- RWKV E1：`runs/bfcl/e1-rwkv7b-baseline-anchor2-c8-v2-20260821`
- RWKV E2：`runs/bfcl/e2-rwkv7b-enhanced-anchor2-c8-v2-20260821`
- Qwen E1：`runs/bfcl/e1-qwen8b-baseline-anchor2-c8-v2-20260821`
- Qwen E2：`runs/bfcl/e2-qwen8b-enhanced-anchor2-c8-v2-20260821`
- 每个正式目录均含 `run.json`、`summary.json`、`trace.jsonl`、`result/` 和官方 `score/*.csv`。
- 无效诊断：`runs/bfcl/e2-qwen8b-enhanced-anchor2-c8-v2-invalid-retry-transcript-20260821`。该轮 wrapped self-contained 首答在纠错 transcript 中重复了 prefill anchor，314/491 不进入正式表。

## 2026-08-19 — Qwen Markdown baseline A+B 全量诊断

- Run:`runs/bfcl/qwen-markdown-baseline-full-c16-t001-20260819`
- 比较组:`M3-baseline-full-diagnostic`
- 模型:`Qwen/Qwen3-8B-FP8`
- Transport:`chat-completions-wrapped`;thinking disabled
- 采样:`top_k=1`,显式有效 temperature `0.01`
- 并发:16;32 并发未通过字节级确定性门禁
- 生成:3641 题,失败/跳过 0/0,严格解析失败 56,耗时 603.35s
- 正样本:2064/2517,82.00%;负样本:115/1124,10.23%
- 主要边界:baseline 的 JSON prefill 对 irrelevance 产生强调用偏置;本轮不是增强档,不得触发 M3 manifest 调整
- 完整报告:`docs/evaluations/bfcl-v4-qwen-markdown-baseline-full-20260819.md`

## 2026-08-18 — RWKV M2.5 wire-format compat 离线重解析

- Run：`runs/bfcl/m2.5-rwkv-wire-compat-v1-20260818`
- 比较组：`M2.5-parser-calibration`
- Source run：`runs/bfcl/m2-smoke-20260818`
- Source trace SHA-256：`9e58772bf8b9fb534e6294e24d3c668d8c38d5ff3ca414993fed91788cbd8b06`
- 模型调用：0；完全复用源运行 400 条原始 `content`
- Parser mode：`rwkv-wire-compat-v1`
- Strict 已接受结果保持不变：125/125，逐条 BFCL result 零差异
- 修复案例：271；仍解析失败：4
- Repair actions：`arguments_unwrapped` 271、`call_id_dropped` 30、`top_level_argument_moved:additional_details` 1、`top_level_argument_moved:type` 1
- 修复案例官方判对：250/271
- 官方成绩：365/400，91.25%
- Strict → compat：115 → 365，增加 250 题、+62.50 pp
- 剩余失败：4 个解析失败、31 个参数类型/取值/可选参数语义错误
- Score：`runs/bfcl/m2.5-rwkv-wire-compat-v1-20260818/score/rwkv-agent-bfcl-ab-v1/non_live/BFCL_v4_simple_python_score.json`
- 完整报告：`docs/evaluations/bfcl-v4-m2.5-wire-compat-20260818.md`

M2.5 证明 M2 的主要损失来自 wire-format 错配,但它不是新一次模型生成,也不是 M4 第六格。compat 若进入最终增强档,必须对 RWKV 与 Qwen Markdown 使用同一实现和配置。

## 2026-08-18 — Qwen Markdown 400 题诊断

- Run：`runs/bfcl/qwen-markdown-baseline-simple-python-400-c16-20260818`
- 比较组：`M2-markdown-single-call`
- 模型：`Qwen/Qwen3-8B-FP8`
- 服务：vLLM `0.27.1`，FP8，NVIDIA GeForce RTX 4060 Ti
- Transport：`chat-completions-wrapped`
- Thinking：`chat_template_kwargs.enable_thinking=false`
- Split/题量：`simple_python`，400
- 并发：16
- 采样：greedy，`top_k=1`，有效 temperature `0.001`
- 每题模型调用：1
- 基础设施失败/跳过：0/0
- 严格 Markdown 解析失败：0
- Prompt/completion tokens：120872/11456
- 总耗时：45.48s；平均请求延迟：1.79s；P50/P95：1.72s/2.58s
- 官方成绩：386/400，96.50%
- 14 道错误均已进入官方 evaluator：4 个 `type_error:nested`、4 个 `value_error:list/tuple`、3 个 `value_error:others`、3 个 `value_error:string`
- Score：`runs/bfcl/qwen-markdown-baseline-simple-python-400-c16-20260818/score/rwkv-agent-bfcl-ab-v1/non_live/BFCL_v4_simple_python_score.json`

与同组 RWKV 运行相比，Qwen 高 67.75 个百分点。该差值表示当前 Harness 下两套“模型 + transport/template”系统的差异，不能全部归因于模型权重。

## 2026-08-18 — RWKV M2 Markdown baseline

- Run：`runs/bfcl/m2-smoke-20260818`
- 比较组：`M2-markdown-single-call`
- 模型：`rwkv7-g1i-7.2b-20260805-ctx16384`
- Transport：RWKV continuation，`/v1/batch/completions`
- Split/题量：`simple_python`，400
- 并发：64
- 采样：greedy，`top_k=1`，有效 temperature `0.001`
- 每题模型调用：1
- 基础设施失败/跳过：0/0
- 严格 Markdown 解析失败：275
- 总耗时：132.19s；平均请求延迟：20.54s；P50/P95：9.85s/45.62s
- 官方成绩：115/400，28.75%
- Score：`runs/bfcl/m2-smoke-20260818/score/rwkv-agent-bfcl-ab-v1/non_live/BFCL_v4_simple_python_score.json`
- 完整验收：`runs/bfcl/m2-acceptance-20260818.md`

该运行完成 M2 正向闭环，但 275 个严格解析失败说明当前主要损失来自 Markdown 调用格式遵循能力。20 题预探针有 1 题出现非字节一致输出，最终矩阵并发下仍需重做确定性门禁。

## 2026-08-18 — Qwen M1 原生 FC 适配器体检

- Run：`runs/bfcl/m1-qwen3-8b-fp8-fixed-20260818`
- 比较组：`M1-native-fc`
- 模型：`Qwen/Qwen3-8B-FP8`
- 服务：vLLM `0.27.1`，FP8，NVIDIA GeForce RTX 4060 Ti
- Transport：`chat-completions-native-fc`
- Splits：`simple_python` 400、`multiple` 200、`live_simple` 258，共 858 题
- 并发：8
- 采样：greedy，`top_k=1`，有效 temperature `0.001`
- 基础设施失败/跳过：0/0
- 总耗时：1202.01s
- 官方成绩：`simple_python` 376/400（94.00%）、`multiple` 188/200（94.00%）、`live_simple` 210/258（81.40%）
- 适配器体检结论：三个 split 与公开 Qwen3-8B FC 数值的差值均在 3.10 个百分点以内，M1 通过
- 完整报告：`runs/bfcl/adapter-health.md`

这组原生 FC 成绩与 M2 Markdown baseline 不属于同一比较组。Qwen 的 94.00% 和 96.50% 分别回答“原生 FC 适配器健康度”和“Markdown 单调用诊断”两个不同问题。

## 2026-08-18 — Qwen 官方 Handler 对照

- Result：`runs/bfcl/m1-official-handler-20260818`
- Score：`runs/bfcl/m1-official-handler-20260818-score`
- 比较组：`M1-official-control`
- 注册模型：`Qwen/Qwen3-8B-FC`；实际服务权重：`Qwen/Qwen3-8B-FP8`
- Handler/transport：固定 evaluator 的 `QwenFCHandler`，手工 tool prompt，`/v1/completions`
- Splits：`simple_python` 400、`multiple` 200、`live_simple` 258，共 858 题
- 并发：8
- 推理错误/null result：0/0
- 总耗时：1402s
- 官方成绩：`simple_python` 381/400（95.25%）、`multiple` 191/200（95.50%）、`live_simple` 217/258（84.11%）
- 与公开 Qwen3-8B FC：三个 split 分别相差 -0.25、-1.00、-0.39 个百分点

该运行用于证明本地 FP8 服务和固定 evaluator 能复现公开模型行为，不代表 RWKV-Agent native adapter 的协议成绩。

## 2026-08-21 — RWKV 后端并发能力探针

- Run：`runs/bfcl/rwkv-probe-concurrency-20260821.py`（探针脚本，含请求格式）
- 对象：`api-129-7b.rwkvos.com`，`rwkv7-g1i-7.2b-20260805-ctx16384`，owned_by=`rwkv_lightning`（Python 后端）
- 结论：**支持并发。** 请求内批量（`contents[]`）是设计主路径：16/32/64/96 路同请求 ≈1.2–1.7s；128 路被 Cloudflare 524 杀掉（约 125s，无响应）。
- 并行 HTTP：≤8 并发全过；16/32 并发有 31–37% 尾部被 CF 524 杀（服务端 FIFO prefill 队列排队超过 CF 限时）。
- 组合：4 并行 × 16 批量 = 64 路总耗时 2.7s，全部 200；SSE 流式批量正常（多 choice delta + `[DONE]`）。
- 服务端机制（上游 `RWKV-Vibe/rwkv_lightning` 源码）：FIFO 票据队列 `acquire_prefill_permit`，并行请求排队不拒绝；单请求超 `max_prefill_bsz` 返回 400 `bsz overflow`；客户端断开返回 499。
- 更正：未解决问题清单 D 节「RWKV endpoint 只能单飞」不适用于本端点（此前观察疑在 CUDA 后端或受客户端超时影响）；矩阵成本不再按单飞估。
- 推荐跑法：`--concurrency 8 --remote-batch-wait 50ms` 让 harness 合并批量（单请求 ≤64 留安全边距）；另外注意 Python urllib 默认 UA 会被 CF 1010 拦截，浏览器 UA 正常。

## 辅助运行索引

## 2026-08-19 — Qwen 原生 FC 官方对齐全量

- Run：`runs/bfcl/qwen-native-fc-full-greedy-t0-c48-m4096-complete-20260819`
- 比较组：`M1-native-fc` 官方对齐参考格
- Transport：`chat-completions-native-fc`
- 题量：13 个 split，共 3641 题；首轮 3503 成功，138 条因 SDK 2 分钟 HTTP timeout 补跑，最终失败/跳过 0/0
- 并发：48；采样：`temperature=0`；最大 completion tokens：4096；per-case timeout：10m；HTTP timeout：11m
- 官方评分：non-live overall 87.85%，live overall 80.01%
- 逐 split 对齐报告：`docs/evaluations/bfcl-v4-qwen-native-fc-alignment-20260819.md`
- 结论：核心 split 与公开 Qwen3-8B FC 值基本在 2pp 内；`live_parallel_multiple` 低 12.50pp，是当前唯一需要单独解释的显著偏差。48 并发提升吞吐，但未消除 FP8/vLLM 动态批处理非确定性。
- **2026-08-20 修正：** 上一条末句的归因方向有误，并发不是不确定性来源；同一份运行报告里「`top_k=1` 未改善稳定性且更慢」的结论亦已撤回。见 `docs/evaluations/bfcl-v4-determinism-concurrency-20260820.md`。

## 2026-08-20 — 确定性归因：并发 vs 解码长度

- Run：`runs/bfcl/qwen-native-nothink-t0-c{1,16,48}-probe-*-20260820`（c1 三轮、c16 六轮、c48 六轮）
- 比较组：确定性诊断，不产出 accuracy，不进矩阵
- 模型/服务：`Qwen/Qwen3-8B-FP8`，vLLM，FP8，RTX 4060 Ti
- Transport：`chat-completions-native-fc`；`chat_template_kwargs.enable_thinking=false`
- Split/题量：`simple_python` 96 题（与 2026-08-19 探针逐 ID 相同）
- 采样：`temperature=0`，max_tokens 4096
- 基础设施失败/跳过：0/0
- 结果：6 轮全稳定题数 c1 **96/96**、c16 94/96、c48 93/96；两两 result 不一致率 c1 0.00%、c16 1.32%、c48 1.60%
- 检验：c16 对 c48 配对精确二项检验 `b=1`、`c=0`、**p=1.000**（旧 2 轮数据同法为 `b=13`、`c=10`、p=0.678）
- 结论：**并发度不是不确定性来源。** 主因是 thinking 拉长解码（输出 p50 36 → 258 token，稳定率 95/96 → 84/96）；次因是「是否发生批处理」的固定底噪，并发 1 时归零，16 与 48 之间无可测差异。完整报告：`docs/evaluations/bfcl-v4-determinism-concurrency-20260820.md`
- 副产物：`--chat-template-thinking` 此前被限制为仅 `chat-completions-wrapped`，本轮开放到原生 FC transport，两条路径共用同一段 `enable_thinking` 推导逻辑

| 日期 | 类型 | 产物 | 结论 |
|---|---|---|---|
| 2026-08-18 | M0 evaluator 冒烟 | `runs/bfcl/result`、`runs/bfcl/score` | 240 条 `irrelevance` 人工空结果闭环，accuracy 1.0；仅验证 evaluator |
| 2026-08-18 | M1 三 split 单题冒烟 | `runs/bfcl/m1-smoke-20260818` | 每个 split 1/1；使用 `--partial-eval`，不作为正式分数 |
| 2026-08-18 | M1 首次 858 题运行 | `runs/bfcl/m1-qwen3-8b-fp8-20260818` | 379/400、190/200、211/258；有 1 个 Unicode 参数名归一化失败，已由 clean run 取代 |
| 2026-08-18 | M2 负向验收 | `runs/bfcl/m2-negative-*-20260818` | `unexpected_param`、`missing_optional`、`type_error:simple` 等错误分支闭环 |
| 2026-08-18 | M2 单题评分探针 | `runs/bfcl/m2-probe3-case0-20260818` | 1/1；子集结果，不作为正式分数 |
| 2026-08-18 | M2 确定性观察 | `runs/bfcl/m2-determinism-*-20260818` | A 轮 7/20；两轮中 19/20 normalized result 相同，尚未满足最终字节一致门禁 |
| 2026-08-18 | Qwen wrapped 单题探针 | `runs/bfcl/qwen-markdown-probe3-case0-20260818` | 禁用 Qwen chat-template thinking 后，正文和严格 parser 恢复正常 |

## 新增条目模板

```markdown
## YYYY-MM-DD — <运行名称>

- Run：`runs/bfcl/<run-id>`
- 比较组：`<group>`
- 模型：`<model>`
- 服务/硬件：`<serving>`
- Transport：`<transport>`
- Split/题量：`<split>`，`<count>`
- 并发：`<concurrency>`
- 采样：`<sampling>`
- 每题模型调用：`<count>`
- 基础设施失败/跳过：`<failed>/<skipped>`
- 严格解析失败：`<count>`
- 总耗时：`<elapsed>`
- 官方成绩：`<correct>/<total>`，`<accuracy>`
- Score：`runs/bfcl/<run-id>/score/.../<score-file>`
- 结论与比较边界：<text>
```
