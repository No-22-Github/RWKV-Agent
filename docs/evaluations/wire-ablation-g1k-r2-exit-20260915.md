# G1K wire 消融：no-tool 出口轮（2026-09-15）

分支 `ablation/g1k-format`。R1.5 示范探针驳回后，本轮按单变量纪律跑在 R1 基座上：
`--profile xml-v1+align-qwen36+no-tool`（`abstain=no-tool`，不带示范）——检验"到底是
框架问题还是出口问题"的关键对照。

no_tool 是协议伪动作：`<tool_call>{"name":"no_tool","arguments":{"reason":...}}`
（aligned 下进 `<tools>` 数组），Runner 不执行、reason/answer 直接成为本轮终答，
评测记 `semantic_no_call`。判分契约：`active_no_call` 要求**整轮零工具步骤**
（`isActiveNoCall` = outcome ∈ {explicit_respond, direct_final, semantic_no_call}
且 `stepTools==0`）——先探索后止损不救分。

## 结果：分数持平 41/60，行为结构大变

| 指标 | R1 align | +no-tool 出口 | Δ |
| --- | --- | --- | --- |
| task_success | 41/60 | 41/60 | 0 |
| irrelevance | 1/20 | 2/20 | +1（irrelevance_11 首步即弃权） |
| missing-required | 20/20 | 19/20 | −1（supplied_5 工具报错后弃权放弃） |
| answer_accuracy | 60/60 | 59/60 | −1（同上） |
| **forced_answers** | **54** | **8** | **−46** |
| model_calls / tool_calls | 276 / 196 | 207 / 126 | −25% / −36% |
| tool_errors / duplicates | 92 / 54 | 42 / 8 | 大幅下降 |
| **全 run 请求字节合计** | **792828** | **606596** | **−23%** |
| 首个 decision prompt（中位） | 2057 B | 2287 B | +230 B（no_tool 目录条目） |
| irrelevance 平均工具调用 | 2.80 | 2.65 | −0.15 |
| protocol_validity | 100% | 99.5% | irrelevance_18 `<think>` 泄漏（G1K 已知习惯，与出口无关） |

irrelevance 20 题的结局分布：called_tool 8、**semantic_no_call 10**、direct_final 1、
decision_protocol_invalid 1。**10 个出口使用里 9 个是先浪费 1-3 步才止损**，只有 1 个
首步即弃权（该题通过）。

## 两条关键轨迹

1. **irrelevance_11（通过）**：首步 `no_tool{"reason":"The user asks for the closest
   integer to 30, which is a simple arithmetic..."}`——出口的预期用法。
2. **bfcl_supplied_simple_python_5（新挂）**：探索 3 步 → search_text 报错 →
   `no_tool{"reason":"...evidence is insufficient"}` **放弃**，丢掉本可读到的
   RELEASE-2048。g1i 时代已知的"弃权滥用"失败模式回归：出口同时是报错后的逃生门。

## 对关键问题的回答

**出口是必要非充分。** 它确实改变了行为——模型"会"用 no_tool 命名弃权了
（10/20），强制 answer 几乎消失（54→8）——但它：
1. 挡不住探索阶段本身（9/10 的弃权发生在浪费 1-3 步之后，判分契约不救分）；
2. 引入工具报错后的放弃模式（−1 missing-required）。

对照 R1.5 示范探针（全阴性、行为不动）：**框架问题和出口问题同时存在**——
没有出口时模型根本停不下来（R0）；有了出口它能停但停得太晚、且偶尔在该干活时停。

## 决定

- **出口保留**为后续轮基座：分数持平（+1/−1 对冲）、总字节 −23%、强制 answer 清零，
  正是本消融要买的"更薄 harness"；弃权滥用是 1 例、可由语料针对。
- 对语料计划的输入：需要两类样本——**首步即弃权**（自明问题零探索）与
  **工具报错后继续/作答而非 no_tool 放弃**的区分样本。
- 产物 `runs/ablation-g1k/r2-notool-exit`。
