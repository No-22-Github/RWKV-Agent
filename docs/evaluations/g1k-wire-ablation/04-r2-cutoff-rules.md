# G1K wire 消融 R2：砍已被证伪的训诫（2026-09-15，结论：驳回）

> [← 返回消融总结](wire-ablation-g1k-summary-20260915.md) | [← 上一轮：no-tool 出口](03-exit-notool.md) | 下一轮：[R3 砍示例块 →](05-r3-bare.md)

分支 `ablation/g1k-format`。按 R0 拆项筛选法，砍掉两条"规则写了但对应错误照样发生"
的训诫句（R0 中均 20/20 违反）：

```
Greetings, thanks, casual conversation, and questions that do not need new tool
evidence must be answered directly. Never invoke tools merely because they are available.
```

失败轮里的报错内容与 duplicate 拒绝通知全部保留（它们是 harness 运行时反馈，不在
Instructions 里）。本轮跑在出口轮基座上：`xml-v1+align-qwen36+no-tool`。

## 结果：40/60（−1），砍除驳回

| 指标 | 出口轮基线 | R2 砍训诫 | Δ |
| --- | --- | --- | --- |
| task_success | 41/60 | 40/60 | **−1** |
| irrelevance | 2/20 | 1/20 | −1（irrelevance_11 翻回） |
| missing-required / multiturn | 19/20 / 20/20 | 19/20 / 20/20 | 0 |
| irrelevance 平均工具调用 | 2.65 | 2.85 | +0.20（更差） |
| 首个 decision prompt（中位） | 2287 B | 2117 B | −170 B |
| 全 run 请求字节合计 | 606596 | 593863 | −12733 B |

端点已证确定性（R0 三遍零翻转），这个 −1 是对字节变更的确定性响应，不是噪声。

## 关键发现：违反率 ≠ 无价值

irrelevance_11 是出口轮里唯一一个**首步即 `no_tool`** 的 case（零探索、通过）。
砍掉 "questions that do not need new tool evidence must be answered directly" 后，
这个 case 失去了 prompt 里唯一直接支持"不调工具直接答"的句子，翻回探索轨迹。
两句训诫被 19/20 的 case 违反，却对 1/20 的正确行为承重——**"规则写了但错误照样
发生"筛选法会把这种弱锚定训诫误判为可砍**。

## 决定

- 按用户判据（掉分必须证明非噪声才换字节）：**驳回砍除，恢复原文**，字节不收。
- 代码已回退（golden prompt 同步回退），本轮 commit 只含本报告；
  运行产物 `runs/ablation-g1k/r2-cut-rules` 供追溯。
- 后续轮基座维持 `xml-v1+align-qwen36+no-tool`（41/60）。
