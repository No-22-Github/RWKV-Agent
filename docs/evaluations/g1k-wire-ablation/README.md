# G1K Wire 格式消融实验专题 (2026-09-15)

> 本专题完整汇总、跨套件定音分数卡与核心教训请直接阅读：
> 👉 [**G1K Wire 消融总结报告 (wire-ablation-g1k-summary-20260915.md)**](wire-ablation-g1k-summary-20260915.md)

---

## 关联关键文档

- **数据侧格式契约**：[`docs/corpus-g1k-wire-format.md`](../../corpus-g1k-wire-format.md)
- **工具调用与对话格式门户**：[`docs/tool-and-wire-formats.md`](../../tool-and-wire-formats.md)
- **Wire 运行时配置指南**：[`docs/wire-configuration.md`](../../wire-configuration.md)

---

## 逐轮消融报告（按实验因果与时序递进）

| 轮次 | 报告文件 | 实验变量 | 核心结论 | 状态 |
| --- | --- | --- | --- | --- |
| **R0** | [00-r0-baseline.md](00-r0-baseline.md) | legacy 基线 ×3 | 40/60，3 遍零抖动确定性；确认失分全在 irrelevance（20/20 发明文件） | 基线确立 |
| **R1** | [01-r1-align.md](01-r1-align.md) | `align=qwen36` | 41/60，User 轮 `<tool_response>` + `<tools>` JSON 数组，梯度良性收窄 | **采纳** |
| **R1.5** | [02-r1.5-probe-nocall.md](02-r1.5-probe-nocall.md) | +实质性 no-call 示范 | 39/60，同事实示范无法唤起直接回答，反而扰动正常题 | 驳回 |
| **出口** | [03-exit-notool.md](03-exit-notool.md) | `abstain=no-tool` | 41/60，forced answer 54→8，字节 −23%，作为后续基座 | **采纳** |
| **R2** | [04-r2-cutoff-rules.md](04-r2-cutoff-rules.md) | 砍已被证伪的训诫 | 40/60，唯一首步弃权 case 翻挂；证明“违反率 ≠ 价值”，弱锚定不可轻杀 | 驳回 |
| **R3** | [05-r3-bare.md](05-r3-bare.md) | `control=bare` | **49/60**，整块砍掉 Examples，消除负迁移，首步调用 18→1/20 | **采纳（最大杠杆）** |
| **R4** | [06-r4-one-stage.md](06-r4-one-stage.md) | `stages=one` | 49/60（零回归），去 `<answer>` 与独立 answer 阶段，全 run 字节 **−56%** | **采纳** |
