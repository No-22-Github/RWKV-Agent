# G1K wire 消融 R4：两阶段合一、去 `<answer>` 包络（2026-09-15，采纳）

分支 `ablation/g1k-format`。R4 = wire 新轴 `stages=one`（`xml-v1+align-qwen36+no-tool+bare+one-stage`），
跑在 R3-bare 基座（49/60）上。口径按修订计划：成本优化立项，验收 = 零回归。

## 实现

- `stages` 轴（`two` 默认 | `one`）：one 模式下 `PrepareAnswer` 不再替换系统块、不再
  预填 `<answer>`，只把"现在用纯文本作答"的 nudge 作为 user 轮追加到**完整决策
  transcript**之后（含 unverified 清单），前缀为空。
- 模型侧从此只活在一个会话形状里（System+`<tools>` 目录+User/Assistant/`<tool_response>`），
  终答是普通文本——与 Markdown 训练格式的收尾方式一致。
- harness 侧仍把该次生成标为 StageAnswer，"answer-now"契约（终答阶段禁止工具动作、
  违规重试）原样生效——模型看到的是单阶段，契约是 harness 内部的。

## 结果：零回归认证通过，路径真实发热一次

| 指标 | R3-bare | R4 one-stage |
| --- | --- | --- |
| task_success | 49/60 | **49/60**（headline 持平） |
| 逐题翻转 | — | 2（irrelevance_19 ↑、21 ↓）＝跨配置批推理抖动 ±2 |
| irrelevance / missing / multiturn | 12/18/19 | 12/18/19（逐类持平） |
| answer_accuracy | 56/59 | 56/59 |
| forced_answers | 0 | 1（irrelevance_16 走到强制点，路径发热） |
| 首个 decision prompt（中位） | 1776 B | 1776 B（决策路径字节零变化） |

发热样本（irrelevance_16）核对：合并 transcript 尾部 = `…</tool_response>` + 拒绝通知
+ nudge 用户轮 + `Assistant:`，**无 answerControl 系统块、无 `<answer>` 预填**；模型在
终答位置仍试图发 `no_tool`，被阶段契约拦截并重试一次（与 two-stage 行为一致）。

## 关于"answer 阶段重发开销"

原计划 R4 的唯一价值是省掉 answer 阶段全 transcript 重发。实测发现这笔开销已经被
前面几轮**提前收走了**：bare+exit 之后 forced_answers≈0，answer 阶段在本套题上整轮
冷置（R3-bare 中 0 次调用），0.81MB→0.34MB 的缩减里已包含这部分。`stages=one` 的
价值是把单阶段纯文本终答**固化为 wire 契约与语料形状**，未来长工具流任务（answer
阶段会发热的场景）直接受益。

## 决定

- **采纳 `stages=one`**。最终基座 canonical：
  `format=xml;transcript=product;transport=text;thinking=off;prefill=none;abstain=no-tool;terminal=none;route=none;catalog=full;control=bare;feedback=raw;subagent=block;align=qwen36;stages=one;loop=…`
  简写 `xml-v1+align-qwen36+no-tool+bare+one-stage`。
- 产物 `runs/ablation-g1k/r4-one-stage`。
- 备注：`--answer-stage-lead` 等单轴旧开关与 `--profile` 的组合校验会拒绝（预期行为），
  未做 smoke 变体。
