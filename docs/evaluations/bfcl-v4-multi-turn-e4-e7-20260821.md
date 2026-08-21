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

使用仓库固定的 RWKV World tokenizer 实际编码完整 prompt：实现为 `third_party/rwkv-mobile/converter/rwkv_src/rwkv_tokenizer.py`，词表为 `rwkv_vocab_v20230424.txt`，SHA-256 `e6dee3d4e31b4d5c40ac99508ac6c701ceef4bed681bf2167ce9a908552bca89`。prompt 包含 initial config、累计 user 消息、GT 调用和官方 backend 的真实 GT 执行结果；不包含 `path`。先按模型标称总窗口 16384 token 计算；runner 每步 `max_tokens=1024`，因此 prompt 预算为 15360 token。

| Split | 全量 catalog tokens p50/p90/p95/max | 全量可行 | 理想 class 收窄 tokens p50/p90/p95/max | 收窄可行 |
|---|---:|---:|---:|---:|
| `base` | 3876/4605/4751/5176 | 200/200 | 2964/3530/4184/4809 | 200/200 |
| `long_context` | 6375/27487/29111/47264 | 158/200 | 5424/26663/28358/46550 | 158/200 |
| `miss_func` | 3895/4623/4769/5194 | 200/200 | 2982/3548/4201/4827 | 200/200 |
| `miss_param` | 3883/4611/4764/5179 | 200/200 | 2967/3530/4193/4825 | 200/200 |

全量 catalog 和理想 class 收窄可行集均为 758/800，因此共同公平集也是 758 题；42 个不可行 case 全部来自 `long_context`。字符数与 token 数在长工具返回上不是稳定比例，先前 3.5 字符/token 得到的 774/783 已废止。CLI 的 `--max-prompt-chars` 只保留为可选 byte guard，默认关闭，不能再用于定义可行集。E7 的 `multi_turn_base_0` 在两套可行集内，既有单题结论不受修正影响。机器可读逐题 token 明细位于 `runs/bfcl-mt/context-budget.json`，摘要位于 `runs/bfcl-mt/context-budget.md`。

考虑到服务实际可用窗口可能小于标称值，又以总上下文 8192 token、仍预留 1024 token 输出、prompt 预算 7168 token 做敏感性重算。token 长度本身不变，仅按更保守阈值重新判定：

| Split | 8K 全量可行 | 8K 理想 class 收窄可行 | 收窄新增 |
|---|---:|---:|---:|
| `base` | 200/200 | 200/200 | 0 |
| `long_context` | 131/200 | 148/200 | 17 |
| `miss_func` | 200/200 | 200/200 | 0 |
| `miss_param` | 200/200 | 200/200 | 0 |
| 合计 | 731/800 | 748/800 | 17 |

因此，“收窄不增加可跑题数”只在 16K 阈值下成立；在保守 8K 阈值下，理想收窄为 17 个 `long_context` case 提供了覆盖扩展。但这个 748 是使用 GT 所需 class 的理论可行上界，不是渐进路由器的实测覆盖：真实路由还可能选错、选多或协议失败。正式 baseline/enhanced 成对评分应冻结共同的 731 题；新增 17 题只能作为 enhanced 的独立覆盖扩展集报告，不能并入成对准确率差值。8K 明细位于 `runs/bfcl-mt/context-budget-8k.json`，摘要位于 `runs/bfcl-mt/context-budget-8k.md`。

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
