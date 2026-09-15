# G1K wire 消融 R1：标签对齐（2026-09-15）

> [← 返回消融总结](wire-ablation-g1k-summary-20260915.md) | [← 上一轮：R0 基线](00-r0-baseline.md) | 下一轮：[R1.5 示范探针 →](02-r1.5-probe-nocall.md)

分支 `ablation/g1k-format`。R1 = wire 新轴 `align=qwen36`（`--profile xml-v1+align-qwen36`），
在 R0 基线（40/60，`align=legacy`）之上只动标签和承载位置：

1. 工具结果从 `Tool: <tool_result>{…}</tool_result>` 改为 user 轮承载
   `User: <tool_response>{…}</tool_response>`（对齐主分支 Markdown 训练格式的 user 轮结果约定）。
2. 工具目录从 markdown 列表改为 `<tools>` 内 JSON 数组（`[\n{…},\n{…}\n]` 布局照搬
   Markdown 格式的目录渲染；条目内容仍是 XML 侧现有 description + flat arguments，一个字不改）。
3. 系统提示词保留在原生 System 模块（现状已符合；`<tools>` 目录随之置于同一 System 块内）。

动作信封 `<tool_call>`、全部指令/训诫文字、示例的事实内容不变。判分兼容：解析器同时接受
新旧两种结果包络，模型回显结果信封记 `envelope_recovered` 修复；answer 校验标签清单补
`<tool_response>`。`align=qwen36` 仅允许 xml+product+text；Markdown 路径零改动。

## 结果（bfcl-product 60 题，1 遍；R0 三遍零翻转已证确定性）

| 指标 | R0 legacy | R1 align | Δ |
| --- | --- | --- | --- |
| task_success | 40/60 | **41/60** | +1 |
| irrelevance | 0/20 | **1/20** | +1（irrelevance_22） |
| missing-required | 20/20 | 20/20 | 0 |
| multiturn | 20/20 | 20/20 | 0 |
| answer_accuracy | 60/60 | 60/60 | 0 |
| protocol_validity | 100% | 100% | 0（新包络零解析失败） |
| **irrelevance 平均工具调用** | **3.65** | **2.80** | **−0.85（−23%）** |
| irrelevance 首步 tool_call | 20/20 | 19/20 | −1 |
| model_calls / tool_calls | 287 / 207 | 276 / 196 | −11 / −11 |
| tool_errors / duplicates / forced | 97 / 57 / 58 | 92 / 54 / 54 | 全降 |
| 首个 decision prompt（中位） | 1974 B | 2057 B | +83 B（`<tools>` 数组更宽） |
| 全 run 请求字节合计 | 812924 B | 792828 B | −20096 B（废步骤减少） |

- 分数 +1 在噪声内，但两个连续量都朝正确方向动：循环深度 −23%，首步直接发调用的
  case 少了一个。这与"对齐让'结果在 user 轮'不再逆着训练先验"的假设一致。
- 零回归：三个满分维度全部保持满分；smoke 对照同日同端点 align 1/10 vs legacy 2/10
  （smoke 对 G1K 本来就难，非 align 特有退化）。
- 字节账：固定前缀略涨 83 B，但每 case 少 1-2 个废步骤，总传输量反降 2.5%。

## 决定

R1 验收通过，作为 R1.5 及后续轮的基座（后续轮全部在 `align=qwen36` 上叠加）。
语料洗洗的格式契约就此钉死：user 轮 `<tool_response>` + `<tools>` JSON 数组 +
原生 System 模块 + `<tool_call>` 动作信封。

## 实现

- `wire` 新轴 `align`（`legacy` 默认 / `qwen36`），修饰符 `align-qwen36`，canonical
  `…;subagent=block;align=qwen36;loop=…`，hash `f3923e8e…`。
- `G1Protocol.AlignQwen36`：目录/示例/结果包络三处字节 + `Parse` 结果信封容错。
- Runner 按轴选结果消息角色（`RoleUser` / `RoleTool`）。
- 产物 `runs/ablation-g1k/r1-align`；smoke 对照 `runs/ablation-g1k/r1-{align,legacy}-smoke`。

## R1.5 探针备注

下一轮在示例块加一条实质性 no-call 示范（`User: 底 10 高 5 的三角形面积是多少？ /
Assistant: 25 平方米。`）。注意该示范与 irrelevance_0（三角形面积 10×5）事实重合：
若 irrelevance_0 翻过，需分辨是行为唤起还是答案搬运——看它是否零工具调用、以及其余
19 题是否跟进。
