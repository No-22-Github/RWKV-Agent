# 蒸馏

蒸馏的计划、报告、题目、老师脚本、工具都在这个目录。每个数据版本占一个文件夹。

```
bench/distill/
  README.md        本页
  common/          跨版本：流程规格、批次登记、排除表、标签映射
  tools/           所有脚本（各版本共用，不按版本复制）
  v1/  v1.3/  v1.4/  v1.41/  v1.42/   1.x = state 调优数据
  v2.0/                              2.x = MiSS 微调（改整个基模）数据
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
| [v1.4](v1.4/) | **已收尾冻结**：3328有效行，train3228 / validation100 | [计划](v1.4/distill-allocation-v1.4.md) | **[收尾与当前统计](v1.4/reports/v1.4-final-20261011.md)**、[历史放量总结](v1.4/reports/v1.4-summary.md) | 8xxx（b10/b13） | b09、b10-pilot/a–e、b11、b13 |
| [v1.41](v1.41/) | **待继续制作**：先修b12样板，承接v1.4缺口 | [计划](v1.41/distill-allocation-v1.41.md)（v1.4 的增量）、**[放量提示（DeepSeek 老师，保留思考）](v1.41/scale-prompt-deepseek.md)** | [现行联合配额](v1.41/reports/v141-allocation-20261011.json)、[10-10历史进度](v1.41/reports/v141-status-20261010.md) | 9xxx（b12） | — |
| [v1.42](v1.42/) | **已出题，待老师跑题**：b14 300 题（bash 200、天气 100），补「调用之后做对」 | [计划](v1.42/distill-allocation-v1.42.md)（v1.41 §4–§5 的增量） | [b14 出题报告](v1.42/reports/b14-authoring.md)、[构成统计](v1.42/reports/b14-stats.json)、[8 字符去重](v1.42/reports/b14-dedup.json) | 10001–10300（b14） | — |
| [v2.0](v2.0/) | **试点，待跑老师**：MiSS 带思考数据；老师无 suffix、每步思考；题目声明 `tool_policy`，目录随机抽、随机排序；按步切行 | [计划](v2.0/distill-allocation-v2.0.md)、[出题规格](v2.0/authoring-v2.0.md) | [b20a](v2.0/reports/b20a-authoring.md)–[b20d](v2.0/reports/b20d-authoring.md)、[b20s 选题](v2.0/reports/b20s-selection.json) | b20s `<前缀>-2xxxx`（1.x 选题）、20001–20140（b20a–c）、nt-21001–21200（b20d） | — |
| [v2.2](v2.2/) | **已出计划，待出题**：在 v2.1 包上修边界（本地搜空→上网、给网址直接读、注入防御、计算器边界、大文件先看规模） | [计划](v2.2/distill-allocation-v2.2.md)、[出题任务书](v2.2/authoring-v2.2.md) | — | 34001–34450（b22a–e） | — |

## common/

- [distill-workflow.md](common/distill-workflow.md)：流水线 S0–S8，出题 → 老师跑 → 抽路径 → 重放 → 打包。
- [harness-corpus-render.md](common/harness-corpus-render.md)：训练行只能由 harness 重放生成。
- [teacher-scripts.md](common/teacher-scripts.md)：老师动作脚本为什么入库、怎么重渲染。
- `batches.jsonl` 批次登记（author 以此为准），`exclude.jsonl` 打包排除表，`tag-map.json` 标签映射（Go 里写死了这个路径），`audit-20260926/` 审阅统计。

## 用法

- 题库根写 `--cases bench/distill`：加载器递归读所有版本的 `cases/`，自动跳过 `cases-shelved/`。只要一个版本就写 `--cases bench/distill/v1.4/cases`。
- 开新版本：建 `v<版本>/`，里面放计划、`reports/`、`cases/`、`teacher/`；脚本仍然放进 `tools/`，见 [tools/README.md](tools/README.md)。
- 9-28 之前的报告里写的是当时的路径（`bench/distill/cases/<场景>/…`、`scripts/…`、`docs/distill/…`），按本页结构换算，报告正文不改。
