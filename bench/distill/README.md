# 蒸馏

蒸馏的计划、报告、题目、老师脚本、工具都在这个目录。每个数据版本占一个文件夹。

```
bench/distill/
  README.md        本页
  common/          跨版本：流程规格、批次登记、排除表、标签映射
  tools/           所有脚本（各版本共用，不按版本复制）
  v1/  v1.3/  v1.4/  v1.41/  v1.42/   1.x = state 调优数据
  v2.0/  v2.1/  v2.2/                2.x = MiSS 微调（改整个基模）数据，v2.3 起按新命名规则开
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
| [v2.1](v2.1/) | **已出包 final-20261018（1545 条，8k/16k 两份）**：老师 Qwen3.7-Flash；三波补题 b21a–b21p；App harness、g1k-think 按步切行 | [计划](v2.1/distill-allocation-v2.1.md)、[第三波任务书](v2.1/authoring-v2.1-wave3.md) | **[出包](v2.1/reports/v2.1-pack-20261017.md)**（§6 是 10-18 正式包）、[b21a](v2.1/reports/b21a-authoring.md)–[b21p](v2.1/reports/b21p-authoring.md)、[v2.1 重放](v2.1/reports/v2.1-work-v3-rerender.md) | 31001–31430、32001–32200（b21a–h）、33001–33770（b21i–p） | — |
| [v2.2](v2.2/) | **已出包 final-20261021（16K，用这个；final-20261020b 已被它取代）**：train 5953 / validation 217 行，2092 条、1669 题（从 20b 剔除 100 道坏轨迹）；agent-tool-v3.0 目录（这个包在 10-21 工具行为修复之前打的，现行目录是 v3.1）；b22a–e 320 题（b22f 长任务 80 题已存档到 cases-shelved/）；b22c 注入题换 Qwen3.8-27B；v2.1 重放保留 5711 行 + 重跑 139 题 | [计划](v2.2/distill-allocation-v2.2.md)、[出题任务书](v2.2/authoring-v2.2.md) | **[出包](v2.2/reports/v2.2-pack-20261020.md)**、[b22c 换老师](v2.2/reports/b22c-teacher.md)、[b22a](v2.2/reports/b22a-authoring.md)–[b22f](v2.2/reports/b22f-authoring.md)、[行修补](v2.2/reports/v2.2-row-fixes.md)、[v2.1 重放](v2.1/reports/v2.1-work-v3-rerender.md) | 34001–34580（b22a–f） | [b22c 附加指令（未采用）](v2.2/teacher/b22c-suffix.txt) |
| [v2.3](v2.3/) | **已出包 v2.3-pack-20261030（2213 条，16K）**：v2.1 为底、v2.2 择优；新批 b23b–g；轨迹闸门剔 328 题；中文 66%、追问 52、≥3 轮 61 未达标，见报告 §4；训练顺序 NoRA → MiSS | [计划](v2.3/distill-allocation-v2.3.md)、[出题任务书](v2.3/authoring-v2.3.md) | **[出包](v2.3/reports/v2.3-pack-20261030.md)**、[b23b](v2.3/reports/b23b-authoring.md)–[b23g](v2.3/reports/b23g-authoring.md) | 35001–35540（b23b–g） | — |

## 命名规则（v2.3 起）

2026-10-21 起新建的目录、包、脚本按下面写；**已有的一个都不改名**（HF 存档仓库、训练机脚本、历史报告和用户的记忆都引用着旧路径）。

| 层级 | 旧样子（一律保留） | 新规则（v2.3 起） |
|---|---|---|
| 版本目录 | `bench/distill/v2.2/` | `bench/distill/v2.3/`（本来就带点，不变） |
| 本地产物目录 | `local/runs/distill/v22/` | `local/runs/distill/v2.3/`，**和 bench 目录同名，保留点号** |
| 训练包 | `final-20261021`、`final-20261020b` | `v2.3-pack-20261101`；同一天第二个包写 `v2.3-pack-20261101-2`；变体加后缀，如 `-ctx16k` |
| 训练脚本 | `train-2-2.sh` | `train-v2.3.sh` |
| 批次号 | `b22a`–`b22f` | 规则不变：`b<主><次><子批字母>`，v2.3 就是 `b23a`… |
| 版本号本身 | `v1.41`、`v1.42`（实为 v1.4 的增量） | 不再出现三段写法：增量版本直接用下一个次版本号 |

**训练产物与权重**（只对以后新建的文件生效，已有权重保持原名）：

| 产物 | 规则 | 例子 |
|---|---|---|
| MiSS / State 权重 | `<基模代号>-<方法>-v<数据版本>-<超参>[-s<步数>]` | `g1l-miss-v2.2-r16-lr2e-5-e2`、`g1k-state-v1.41-lr1e-2-s1224` |
| 上游官方权重 | 保持上游原名 | `rwkv7-g1k-7.2b-20260930-ctx25600`、`rwkv-g1l-7b-temp-3797` |
| 服务端注册的 state / adapter id | 由服务端生成，不管 | — |

权重名里出现模型代号（g1k、g1l）是对的：权重本来就属于某一代基模。要从名字里去掉模型代号的，只是 **wire 格式**（`agent-wire-v1.0`）和 **采样预设**（`agent-default` 等）的名字。

## common/

- [distill-workflow.md](common/distill-workflow.md)：流水线 S0–S8，出题 → 老师跑 → 抽路径 → 重放 → 打包。
- [harness-corpus-render.md](common/harness-corpus-render.md)：训练行只能由 harness 重放生成。
- [teacher-scripts.md](common/teacher-scripts.md)：老师动作脚本为什么入库、怎么重渲染。
- `batches.jsonl` 批次登记（author 以此为准），`exclude.jsonl` 打包排除表，`tag-map.json` 标签映射（Go 里写死了这个路径），`audit-20260926/` 审阅统计。

## 用法

- 题库根写 `--cases bench/distill`：加载器递归读所有版本的 `cases/`，自动跳过 `cases-shelved/`。只要一个版本就写 `--cases bench/distill/v1.4/cases`。
- 开新版本：建 `v<版本>/`，里面放计划、`reports/`、`cases/`、`teacher/`；脚本仍然放进 `tools/`，见 [tools/README.md](tools/README.md)。
- 9-28 之前的报告里写的是当时的路径（`bench/distill/cases/<场景>/…`、`scripts/…`、`docs/distill/…`），按本页结构换算，报告正文不改。
