# 蒸馏文档

按数据版本分目录。每个版本目录里：`distill-allocation-v*.md` 是计划，其余是执行提示和批次报告。
题目、老师脚本、构建工具在 [`bench/distill/`](../../bench/distill/README.md)，同样按版本分目录。

| 版本 | 状态 | 计划 | 执行提示 / 规格 | 报告 | 题号段 |
| --- | --- | --- | --- | --- | --- |
| [v1/](v1/) | 已完成（v1.0–v1.2） | [distill-allocation-v1.md](v1/distill-allocation-v1.md) | [b04 规格](v1/distill-b04-glm.md)、[09-29 修数派单](v1/fix-20260929-glm.md) | [smoke](v1/smoke.md)、[b01](v1/b01.md)–[b04](v1/b04.md)、[判据形状复核](v1/verify-shape-review-20260929.md) | 5xxx（b01–b03）、6xxx（b04） |
| [v1.3/](v1.3/) | 已完成 | [distill-allocation-v1.3.md](v1.3/distill-allocation-v1.3.md) | — | [b05](v1.3/b05.md)–[b08](v1.3/b08.md)、[数据集](v1.3/dataset-v13.md)、[清洗](v1.3/clean-v13.md) | 7xxx |
| [v1.4/](v1.4/) | M0–M2 完成，M3 放量未开始 | [distill-allocation-v1.4.md](v1.4/distill-allocation-v1.4.md) | [b10 放量提示](v1.4/b10-scale-prompt.md)、[b10 解题简报](v1.4/b10-solver-brief.md) | [b09](v1.4/b09-report.md)、[b10 试跑](v1.4/b10-pilot.md) | 8xxx（b10） |
| [v1.41/](v1.41/) | **进行中**：样板就绪，放量未开始 | [distill-allocation-v1.41.md](v1.41/distill-allocation-v1.41.md)（v1.4 的增量） | 放量照 v1.4 的 [b10 放量提示](v1.4/b10-scale-prompt.md) §7 | [10-10 进度重估](v1.41/v141-status-20261010.md) | 9xxx（b12） |

跨版本通用的规格放在本目录根：

- [distill-workflow.md](distill-workflow.md)：流水线 S0–S8，出题 → 老师跑 → 抽路径 → 重放 → 打包。
- [harness-corpus-render.md](harness-corpus-render.md)：训练行只能由 harness 重放生成。

新版本照这个样子开目录：`docs/distill/v<版本>/`、`bench/distill/cases/v<版本>/`、`bench/distill/scripts/v<版本>/`、`bench/distill/tools/v<版本>/`。
