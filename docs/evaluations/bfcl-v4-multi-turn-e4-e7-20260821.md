# BFCL v4 multi-turn E4–E7 实验记录

日期：2026-08-21

数据：BFCL v4 commit `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`

evaluator：`bfcl-eval==2026.3.23`

本文记录多轮 M0–M3 的实现与验收。Go Harness 负责生成、解析、持久会话、工具执行回喂与结果落盘；最终正确与否只采用固定版本官方 evaluator 的判定。

## E4：上游语义核对

- `STATELESS_CLASSES` 只有 `MathAPI`。
- `method_invoke_order_checker` 仍未启用；`path` 只进入 trace 的 `path_diagnostic`，不进入 prompt。
- 官方循环每轮最多 20 step，工具结果逐 step 回喂，模拟器实例跨 step/turn 保活。
- holdout 轮使用固定追加函数提示并重新编译工具表；`missed_function` 到指定轮才释放，`excluded_function` 始终剔除。
- state checker 忽略以下划线开头的私有属性；整题判分仍是状态、响应与空轮规则的全有全无结果。
- 工具定义给模型前删除仅供模拟器描述返回结构的 `response` 字段，执行仍使用官方 backend。
- 数据中 `base` 和 `long_context` 各有 3 个单轮 case；loader 因此接受至少一轮，而不是错误地假设至少两轮。

## E5：800 题上下文普查

估算使用 3.5 字符/token，RWKV 可用预算 12288 token，即 43008 字符。prompt 规模包含 initial config、累计 user 消息、GT 调用和官方 backend 的真实 GT 执行结果；不包含 `path`。

| Split | 全量 catalog p50/p90/p95/max | 全量可行 | 理想 class 收窄 p50/p90/p95/max | 收窄可行 |
|---|---:|---:|---:|---:|
| `base` | 16472/19848/20326/21687 | 200/200 | 12652/14512/18746/20618 | 200/200 |
| `long_context` | 24063/56297/58852/83591 | 157/200 | 19171/50015/57047/80382 | 160/200 |
| `miss_func` | 16549/19926/20404/21765 | 200/200 | 12719/14590/18359/20696 | 200/200 |
| `miss_param` | 16485/19870/20364/21728 | 200/200 | 12690/14535/18746/20670 | 200/200 |

全量 catalog 可行集为 757/800，理想收窄可行集为 760/800；后续 baseline/enhanced 公平比较应冻结二者共同的 757 题。E7 的 `multi_turn_base_0` 在两套可行集内。机器可读明细位于 `runs/bfcl-mt/context-budget.json`，摘要位于 `runs/bfcl-mt/context-budget.md`。

## E6：sidecar 与 GT 门禁

新增 JSONL Python sidecar，只暴露 `new`、`execute`、`close`、`shutdown`；每个 session 使用官方 `execute_multi_turn_func_call`，实例跨调用保活。运行时代码不读取答案文件，并由 Go 测试检查这一依赖边界。

- 正向：`multi_turn_base` 200/200 个 GT case 均完成 sidecar 执行，执行错误 0；官方 evaluator 200/200，100%。
- 负向：对 `multi_turn_base_0` 多执行 `mkdir(dir_name='unexpected_extra')`，官方 evaluator 0/1，错误为 `multi_turn:instance_state_mismatch`。
- 输出形状为官方需要的 `list[list[list[str]]]`。

产物：`runs/bfcl-mt/e6-gt-selftest-v2`。

## E7：`multi_turn_base_0` 单题闭环

闭环均实际经过“模型生成 → 调用解析 → sidecar 持久执行 → 工具结果回喂 → BFCL 嵌套结果 → 官方 evaluator”。Baseline 使用全量 catalog、strict parser、无救援；enhanced 接入产品渐进路由、wire compat、一次纠错、重复拒绝、循环救援和执行错误回喂。

| 模型/档位 | 轮/step | 模型调用 | 最大 prompt | Harness 结果 | 官方结果 |
|---|---:|---:|---:|---|---:|
| Qwen baseline | 4/6 | 6 | 19113 B | 4 轮均 strict parse error；无效 assistant 输出按官方语义保留到后续轮 | 0/1，`empty_turn_model_response` |
| Qwen enhanced | 4/38 | 45（含 7 次 route） | 17158 B | 4 次 route decision、3 次 route retry、1 次重复拒绝、4 次 loop rescue | 0/1，`instance_state_mismatch` |
| RWKV baseline | 4/4 | 4 | 27330 B | 4 轮均输出非 JSON Agent 文本并 strict parse error | 0/1，`empty_turn_model_response` |
| RWKV enhanced | 1/0 | 2（均为 route） | 0 B | 两次输出均带前置说明且 route envelope 未闭合，纠错上限后终止 | 0/1，`force_terminated` |

Qwen enhanced 确实执行了 38 个 step 并跨轮保持模拟器状态，但首轮把 `temp` 建在错误目录，后续又在目录导航中循环，最终公开状态与 GT 不同。RWKV baseline 的主要问题在调用协议遵循；enhanced 的失败更早发生在渐进路由协议，原始路由输出已进入事件 trace。四组官方 partial evaluator 均正常退出并写出 score；由于上游单样本 latency 聚合会调用 `statistics.stdev`，单题官方 result 不带 latency，完整时延仍保存在 `trace.jsonl` 和 `summary.json`。

正式 E7 辅助产物：

- `runs/bfcl-mt/e7-qwen8b-baseline-base0-v4-20260821`
- `runs/bfcl-mt/e7-qwen8b-enhanced-base0-v4-20260821`
- `runs/bfcl-mt/e7-rwkv7b-baseline-base0-v4-20260821`
- `runs/bfcl-mt/e7-rwkv7b-enhanced-base0-v5-20260821`

Qwen 服务注册名是 `Qwen/Qwen3-8B-FP8`；实验未独立核验用户所述 int8 与服务注册名 FP8 的差异。E7 是单题基础设施与 Agent 循环验收，0/1 结果不应外推为模型多轮总成绩；正式能力比较需要 E8 的冻结共同可行样本。
