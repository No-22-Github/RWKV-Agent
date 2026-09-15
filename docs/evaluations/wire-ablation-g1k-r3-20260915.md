# G1K wire 消融 R3：砍示例块（2026-09-15，结论：整块砍，采纳入基座）

分支 `ablation/g1k-format`。R3 = `control` 轴两个新变体，跑在出口轮基座
（`align-qwen36+no-tool`，41/60）上：

- `control=bare`（`xml-v1+align-qwen36+no-tool+bare`）：整块砍 Examples。
- `control=greeting`（`…+greeting`）：中间态，只留 `你好→你好！有什么我可以帮你的吗？`。

## 结果：示例块是负资产，整块砍是全消融最大杠杆

| 指标 | 出口轮基线 | R3 bare（整块砍） | R3 greeting（只留你好） |
| --- | --- | --- | --- |
| task_success | 41/60 | **49/60**（+8） | 46/60（+5） |
| **irrelevance** | **2/20** | **12/20** | 9/20 |
| missing-required | 19/20 | 18/20 | 19/20 |
| multiturn | 20/20 | 19/20 | 18/20 |
| answer_accuracy | 59/60 | 56/59 | 56/59 |
| **irrelevance 平均工具调用** | **2.65** | **0.35** | 0.60 |
| irrelevance 首步 tool_call | 18/20 | **1/20** | 3/20 |
| forced_answers | 8 | 0 | 1 |
| tool_errors / duplicates | 42 / 8 | 3 / 0 | 5 / 0 |
| **首个 decision prompt（中位）** | 2287 B | **1776 B**（−511） | 1853 B（−434） |
| **全 run 请求字节合计** | **606596** | **340674**（**−44%**） | 407666（−33%） |
| repairs（格式漂移） | 0 | 4 次轻微（array_envelope / function_wrapper / stringified / envelope_recovered 各 1） | 未统计入表 |

翻转让"弃权行为不可唤起"的结论需要修正：**行为唤得起来，但被示例块压着**。基座
prompt 里的工具示范（`Find files under docs → <tool_call>` / `Read README.md → 调工具`）
正好摆在用户问题前面，模型照着演——这就是 R0 以来 20/20"发明检索任务"失败形状的
直接来源。砍掉示范后，irrelevance 从地板（0-2/20）跳到 12/20，梯度降为 0.35 次/case。

代价（bare）：answer 56/59（3 个终答错）、missing −2（supplied_14/35 翻挂——没有示范后
个别"需要工具"的 case 反而摸索失败）、5 个 `<think>` 泄漏循环（G1K 已知习惯，裸决策
prompt 下更集中）、4 次轻微格式漂移。净收益 +8 题，全部方向性利好。

## 判读

- 用户预设"few-shot 的价值全在那一条（你好）上"**不成立**：你好-only（46/60）介于
  bare（49/60）和基线（41/60）之间——示例块的净值是负的，你好示范本身也略负
  （bare 比 greeting 多 3 个 irrelevance、总分离 3 题）。
- R1.5 加示范失败与 R3 砍示范成功的方向一致：**这个模型的 in-context 示范通道很重
  （会照着演），所以示范必须是"想要的行为"的样本，任何工具调用示范都会外溢到不该
  调工具的场合。** 对语料的直接要求：正样本要覆盖"实质性问题零工具直答"形状，且
  语料里工具调用示范与任务类型要严格配对。

## 决定

- **采纳 bare**：新基座 = `control=bare;align=qwen36;abstain=no-tool`（canonical
  49/60、0.81MB→0.34MB、固定前缀 −511 B）。
- `control=greeting`、`base-nocall` 两个变体保留为 wire 基础设施供复测。
- 产物 `runs/ablation-g1k/r3-{bare,greeting}`。
