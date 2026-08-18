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
| `validation-only` | 固定 evaluator 与人工构造结果 | 数据、目录、decoder 和错误分支是否闭环 | 模型能力 |

`M2-markdown-single-call` 中，RWKV 直接接收 continuation prompt；Chat Completions 模型还会经过 wrapped system instruction 和服务端 chat template，并受最多 4 个 stop sequence 的接口限制，而 RWKV M2 使用 5 个。因此该组具有强诊断可比性，但不是 transport/template 完全一致的模型级隔离实验。

## 正式评分总表

| 日期 | Run | 比较组 | 模型 | Split | 正确/总数 | 准确率 | 并发 | 解析失败 | 耗时 |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| 2026-08-18 | `qwen-markdown-baseline-simple-python-400-c16-20260818` | `M2-markdown-single-call` | Qwen3-8B-FP8 | `simple_python` | 386/400 | 96.50% | 16 | 0 | 45.48s |
| 2026-08-18 | `m2-smoke-20260818` | `M2-markdown-single-call` | RWKV7 G1i 7.2B | `simple_python` | 115/400 | 28.75% | 64 | 275 | 132.19s |
| 2026-08-18 | `m1-qwen3-8b-fp8-fixed-20260818` | `M1-native-fc` | Qwen3-8B-FP8 | `simple_python` | 376/400 | 94.00% | 8 | 0 | 1202.01s 三个 split 合计 |
| 2026-08-18 | `m1-qwen3-8b-fp8-fixed-20260818` | `M1-native-fc` | Qwen3-8B-FP8 | `multiple` | 188/200 | 94.00% | 8 | 0 | 1202.01s 三个 split 合计 |
| 2026-08-18 | `m1-qwen3-8b-fp8-fixed-20260818` | `M1-native-fc` | Qwen3-8B-FP8 | `live_simple` | 210/258 | 81.40% | 8 | 0 | 1202.01s 三个 split 合计 |
| 2026-08-18 | `m1-official-handler-20260818` | `M1-official-control` | Qwen3-8B-FP8 | `simple_python` | 381/400 | 95.25% | 8 | N/A | 1402s 三个 split 合计 |
| 2026-08-18 | `m1-official-handler-20260818` | `M1-official-control` | Qwen3-8B-FP8 | `multiple` | 191/200 | 95.50% | 8 | N/A | 1402s 三个 split 合计 |
| 2026-08-18 | `m1-official-handler-20260818` | `M1-official-control` | Qwen3-8B-FP8 | `live_simple` | 217/258 | 84.11% | 8 | N/A | 1402s 三个 split 合计 |

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

## 辅助运行索引

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
