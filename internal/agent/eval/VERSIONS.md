# 评测版本变更表

`run.json` 里的 `harness.version`、`harness.scorer_version`、`harness.outcome_taxonomy_version`
决定两次跑分能不能直接比。**只有评测或判分行为变了、分数可能变时才往上加整数**；
改名字、改注释、改帮助文字不加。工具目录的版本规则见
[`internal/agent/product/catalog_version.go`](../product/catalog_version.go)
（`agent-tool-v3.1`；主版本号变了模型看到的工具描述就变了）。

## 版本写法与语义

| 对象 | 写法 | 主版本号 | 次版本号 | 哈希 |
|---|---|---|---|---|
| 工具目录 | `agent-tool-v3.1` | 工具名、描述、参数、schema 变了 | 只改工具行为 | `tool_catalog_hash`：主版本变它才变 |
| wire 格式 | `agent-wire-v1.0` | 模型看到的提示词或协议格式变了 | 解析容错、兜底等不进 canonical 的行为 | `wire_hash`：主版本变它才变 |
| 考卷 | `agent-exam-v1.0` | 增删题 | 修订题面或判据 | `exam_hash`：两种情况都会变 |
| harness / scorer / outcome | `rwkv-agent-eval-v22` 等 | 只往上加整数：评测或判分行为变了、分数可能变时才加 | — | — |
| schema_version | 整数 | 只往上加整数：记录格式不兼容时才加 | — | — |
| 蒸馏数据 | `v2.3` | 训练配方或格式大改 | 加批次、修数据 | — |

历史行由 `git log -S` 考古得出；提交信息没说清改了什么的那一代写
`未知（提交信息无说明）`，不根据代码 diff 猜。这张表以后会被拿来解释分数变化，
编出来的条目比空着更有害。**对分数的影响**一栏目前没有可靠记录，统一写
`未知（未记录）`；有了对照实验再补。

## harness

| harness | 日期 | 提交 | 改了什么（一句话） | 对分数的影响 |
|---|---|---|---|---|
| `rwkv-agent-eval-v18` | 2026-08-26 | `4adad5be` | 路由提示词的框架显式化，使之可复现 | 未知（未记录） |
| `rwkv-agent-eval-v19` | 2026-08-26 | `7b068359` | 判分区分「主动弃权」与「协议失败」 | 未知（未记录） |
| `rwkv-agent-eval-v20` | 2026-08-28 | `e0047792` | 产品 harness 对齐 G1I 的行为偏好 | 未知（未记录） |
| `rwkv-agent-eval-v21` | 2026-09-17 | `665c166e` | workbank 收尾 Part A：重跑前修测量缺陷 | 未知（未记录） |
| `rwkv-agent-eval-v22` | 2026-09-25 | `1d92d15d` | md-fence 解析器不再把终答从第一个围栏处截断 | 未知（未记录） |

本仓库可检索的常量历史从 v17→v18 开始；更早的版本没有可核对的提交。

## scorer

| scorer | 日期 | 提交 | 改了什么（一句话） | 对分数的影响 |
|---|---|---|---|---|
| `rwkv-agent-eval-scorer-v1` | 2026-08-26 | `7b068359` | 引入独立判分器版本，并分类主动弃权/协议失败 | 未知（未记录） |
| `rwkv-agent-eval-scorer-v2` | 2026-09-17 | `665c166e` | 随 workbank 收尾 Part A 的测量缺陷修复升级 | 未知（未记录） |
| `rwkv-agent-eval-scorer-v3` | 2026-09-21 | `85e7dc6c` | 判分对象改为模型行为而非 harness 行为 | 未知（未记录） |

## outcome

| outcome | 日期 | 提交 | 改了什么（一句话） | 对分数的影响 |
|---|---|---|---|---|
| `rwkv-agent-outcome-v1` | 2026-08-26 | `7b068359` | 引入 outcome 分类法 | 未知（未记录） |
| `rwkv-agent-outcome-v2` | 2026-08-28 | `e0047792` | 未知（提交信息无说明） | 未知（未记录） |

## 备注

- 2026-10-21 的版本改名（wire `g1k` → `agent-wire-v1.0`、考卷 `exam-full` →
  `agent-exam-v1.0`、采样预设 `g1k-agent` → `agent-default`）只换标签，评测行为不变，
  所以 harness 仍是 v22，不加 v23。
