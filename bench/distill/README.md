# 蒸馏

蒸馏的计划、报告、题目、老师脚本、工具都在这个目录。每个数据版本占一个文件夹。

```
bench/distill/
  README.md        本页
  common/          跨版本：流程规格、批次登记、排除表、标签映射
  tools/           所有脚本（各版本共用，不按版本复制）
  v1/  v1.3/  v1.4/  v1.41/
    distill-allocation-v*.md   这个版本的计划（以及执行提示、规格）
    reports/                   批次报告
    cases/<场景>/<题号>/        题目（case.json + verify.py + NOTES.md）
    teacher/                   老师动作脚本 *.jsonl（corpus render --script 的输入）、老师附加指令 *-suffix.txt
```

## 各版本

| 版本 | 状态 | 计划 / 执行提示 | 报告 | 题目 | 老师脚本 |
| --- | --- | --- | --- | --- | --- |
| [v1](v1/) | 已完成（v1.0–v1.2） | [计划](v1/distill-allocation-v1.md)、[b04 规格](v1/distill-b04-glm.md)、[09-29 修数派单](v1/fix-20260929-glm.md) | [smoke](v1/reports/smoke.md)、[b01](v1/reports/b01.md)–[b04](v1/reports/b04.md)、[判据形状复核](v1/reports/verify-shape-review-20260929.md) | 5xxx（b01–b03）、6xxx（b04），下架题在 `v1/cases-shelved/` | base700、b01–b04、b04r |
| [v1.3](v1.3/) | 已完成 | [计划](v1.3/distill-allocation-v1.3.md) | [b05](v1.3/reports/b05.md)–[b08](v1.3/reports/b08.md)、[数据集](v1.3/reports/dataset-v13.md)、[清洗](v1.3/reports/clean-v13.md) | 7xxx | b05-baseline、b05–b07 |
| [v1.4](v1.4/) | M0–M2 完成，M3 放量未开始 | [计划](v1.4/distill-allocation-v1.4.md)、[b10 放量提示](v1.4/b10-scale-prompt.md)、[b10 解题简报](v1.4/b10-solver-brief.md) | [b09](v1.4/reports/b09-report.md)、[b10 试跑](v1.4/reports/b10-pilot.md) | 8xxx（b10） | b09-m1、b10-pilot |
| [v1.41](v1.41/) | **进行中**：样板就绪，放量未开始 | [计划](v1.41/distill-allocation-v1.41.md)（v1.4 的增量），放量照 [b10 放量提示](v1.4/b10-scale-prompt.md) §7 | [10-10 进度重估](v1.41/reports/v141-status-20261010.md) | 9xxx（b12） | — |

## common/

- [distill-workflow.md](common/distill-workflow.md)：流水线 S0–S8，出题 → 老师跑 → 抽路径 → 重放 → 打包。
- [harness-corpus-render.md](common/harness-corpus-render.md)：训练行只能由 harness 重放生成。
- [teacher-scripts.md](common/teacher-scripts.md)：老师动作脚本为什么入库、怎么重渲染。
- `batches.jsonl` 批次登记（author 以此为准），`exclude.jsonl` 打包排除表，`tag-map.json` 标签映射（Go 里写死了这个路径），`audit-20260926/` 审阅统计。

## 用法

- 题库根写 `--cases bench/distill`：加载器递归读所有版本的 `cases/`，自动跳过 `cases-shelved/`。只要一个版本就写 `--cases bench/distill/v1.4/cases`。
- 开新版本：建 `v<版本>/`，里面放计划、`reports/`、`cases/`、`teacher/`；脚本仍然放进 `tools/`，见 [tools/README.md](tools/README.md)。
- 9-28 之前的报告里写的是当时的路径（`bench/distill/cases/<场景>/…`、`scripts/…`、`docs/distill/…`），按本页结构换算，报告正文不改。
