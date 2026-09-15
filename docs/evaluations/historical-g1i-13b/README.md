# G1I 13B / P0 早期评测与 Harness 修复历史 (2026-08-03 ~ 2026-08-06)

> 本目录收录 2026 年 8 月初在 RWKV G1i 13B 系列模型（`rwkv-g1i-13b-4922` 与 `rwkv7-g1i-13.3b-20260805-ctx16384`）上进行的早期 Agent 探索与 Harness 修复评测。

---

## 核心历史结论

1. **模型没变，Harness 把 boundary 从 4/18 做到 13/18**：早期 13B 模型本身具备基本的控制面协议能力，但极其容易受到不合理 Harness 机制与工具契约的干扰。
2. **“不合身的工具比没有工具更差”**：在 v9 修复中，撤除原以为能辅助计算的 `structured_query` 后，模型仅用 `read_file` 就答对了原本算错的题目。
3. **P0 本地助手闭环**：验证了本地助手的降级与协议安全性，明确了复杂财务与多步计算的出口门槛。

详细复盘见成果长篇报告：[`docs/reports/harness-layer-optimization-report.html`](../../reports/harness-layer-optimization-report.html)。

---

## 报告清单

| 文档 | 日期 / 模型 | 核心发现 |
| --- | --- | --- |
| [api-13b-evaluation-report-20260803.md](api-13b-evaluation-report-20260803.md) | 2026-08-03 / 13B 4922 | 早期 13B Harness 实测问题报告，boundary 10/18，暴露重复调用与算术瓶颈 |
| [local-assistant-p0-effect-report-20260804.md](local-assistant-p0-effect-report-20260804.md) | 2026-08-04 / 13B 4922 | 本地优先助手 Agent P0 落地效果报告，确定性工具闭环但算术 0/5 未达标 |
| [api-13b-v8-evaluation-report-20260805.md](api-13b-v8-evaluation-report-20260805.md) | 2026-08-05 / 13.3B 0805 | 13.3B 评测（v8 profile），主 boundary 持平 8/18，助手事实链有进步 |
| [api-13b-v9-evaluation-report-20260806.md](api-13b-v9-evaluation-report-20260806.md) | 2026-08-06 / 13.3B 0805 | Harness 三项修复复测：严格任务 8→10/18，答案 9→12/18，发现 `structured_query` 负作用 |
