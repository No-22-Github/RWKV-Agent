# 评测版本变更表

`run.json` 里的 `harness.version`、`harness.scorer_version`、`harness.outcome_taxonomy_version`
决定两次跑分能不能直接比。**只有评测或判分行为变了、分数可能变时才往上加整数**；
改名字、改注释、改帮助文字不加。工具目录的版本规则见
[`internal/agent/product/catalog_version.go`](../product/catalog_version.go)
（`agent-tool-v3.2`；主版本号变了模型看到的工具描述就变了）。

## 版本写法与语义

| 对象 | 写法 | 主版本号 | 次版本号 | 哈希 |
|---|---|---|---|---|
| 工具目录 | `agent-tool-v3.2` | 工具名、描述、参数、schema 变了 | 只改工具行为 | `tool_catalog_hash`：主版本变它才变 |
| wire 格式 | `agent-wire-v1.0` | 模型看到的提示词或协议格式变了 | 解析容错、兜底等不进 canonical 的行为 | `wire_hash`：主版本变它才变 |
| 考卷 | `agent-exam-v1.2` | 增删题 | 修订题面或判据 | `exam_hash`：两种情况都会变 |
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
| `rwkv-agent-eval-v4` | 2026-07-30 | `ace2c135` | 引入 Agent 评测 harness（仓库里能查到的第一代） | 未知（未记录） |
| `rwkv-agent-eval-v5` | 2026-08-01 | `205f8fc8` | 加强工具调用失败后的恢复 | 未知（未记录） |
| `rwkv-agent-eval-v7` | 2026-08-02 | `633cf995` | 加强证据校验（v5 → v7 跳号） | 未知（未记录） |
| `rwkv-agent-eval-v8` | 2026-08-04 | `d09fba22` | 加入本地助手 P0 harness | 未知（未记录） |
| `rwkv-agent-eval-v10` | 2026-08-10 | `12d745d9` | boundary 判分接受等价的检索工具路径（v8 → v10 跳号） | 未知（未记录） |
| `rwkv-agent-eval-v12` | 2026-08-13 | `c94a35b3` | 内置 Primitive Bench 评测套件（v10 → v12 跳号） | 未知（未记录） |
| `rwkv-agent-eval-v13` | 2026-08-13 | `a4687aaf` | 加入原生 G1i primitive bench 协议 | 未知（未记录） |
| `rwkv-agent-eval-v14` | 2026-08-13 | `31d756dd` | 加入 Go 原生 primitive 工具档案 | 未知（未记录） |
| `rwkv-agent-eval-v15` | 2026-08-13 | `f066e5ae` | 加强原生工具循环的控制 | 未知（未记录） |
| `rwkv-agent-eval-v16` | 2026-08-13 | `0afb531c` | 提交答案时保留原样证据 | 未知（未记录） |
| `rwkv-agent-eval-v17` | 2026-08-13 | `53d32d6e` | 加入可选的表格工具和工作区修订号 | 未知（未记录） |
| `rwkv-agent-eval-v18` | 2026-08-26 | `4adad5be` | 路由提示词的框架显式化，使之可复现 | 未知（未记录） |
| `rwkv-agent-eval-v19` | 2026-08-26 | `7b068359` | 判分区分「主动弃权」与「协议失败」 | 未知（未记录） |
| `rwkv-agent-eval-v20` | 2026-08-28 | `e0047792` | 产品 harness 对齐 G1I 的行为偏好 | 未知（未记录） |
| `rwkv-agent-eval-v21` | 2026-09-17 | `665c166e` | workbank 收尾 Part A：重跑前修测量缺陷 | 未知（未记录） |
| `rwkv-agent-eval-v22` | 2026-09-25 | `1d92d15d` | md-fence 解析器不再把终答从第一个围栏处截断 | 未知（未记录） |
| `rwkv-agent-eval-v23` | 2026-10-23 | `57f55c66` | 没有 `<tool_call>` 包裹的 JSON 一律当正文：不再报"缺信封"协议错，作答阶段不再当工具调用，终答不再被当成 JSON 违规换成兜底话术 | 42 遍旧 run 里触发过 json_payload 9 次、缺信封 4 次；需新跑分才能看到 |
| `rwkv-agent-eval-v24` | 2026-10-29 | 待提交 | `<tool_call>` 里接受 OpenAI 外壳 `{"type":"function","function":{…}}` 和完整对象后多出的 `}`（含"思考后先说话"兜底路径） | G1L 思考两遍（irwkv-think-20261029）里两类合计约 229 步被拒；需新跑分才能看到 |

考古命令（不限文件路径：早期常量定义在别的文件里，只搜 `types.go` 会漏掉 v4–v17）：
`git log --reverse -G '"rwkv-agent-eval-v[0-9]+"' -- '*.go' ':!*_test.go'`，再看每个提交新增的常量定义行。
v1–v3、v6、v9、v11 在仓库历史里没有出现过：常量第一次提交（`ace2c135`）时已经是 v4；v6、v9、v11 是两次提交之间连升了两代，中间那一代从没提交过。

## scorer

| scorer | 日期 | 提交 | 改了什么（一句话） | 对分数的影响 |
|---|---|---|---|---|
| `rwkv-agent-eval-scorer-v1` | 2026-08-26 | `7b068359` | 引入独立判分器版本，并分类主动弃权/协议失败 | 未知（未记录） |
| `rwkv-agent-eval-scorer-v2` | 2026-09-17 | `665c166e` | 随 workbank 收尾 Part A 的测量缺陷修复升级 | 未知（未记录） |
| `rwkv-agent-eval-scorer-v3` | 2026-09-21 | `85e7dc6c` | 判分对象改为模型行为而非 harness 行为 | 未知（未记录） |
| `rwkv-agent-eval-scorer-v4` | 2026-10-23 | `ac2405a8` | 判分审计：summary 兜底不算模型答案；包含类检查不分大小写、去 `**`（排除项仍分大小写）；首行以冒号结尾时看其后首末行；`expected_number_in_text` 只读首末行、加粗行和答案标记后；新增 `output_contains_in_order`；文件 equals 容忍末尾换行 | 见 `docs/evaluations/exam-v12-rescore-20261023/`（离线重判） |

## outcome

| outcome | 日期 | 提交 | 改了什么（一句话） | 对分数的影响 |
|---|---|---|---|---|
| `rwkv-agent-outcome-v1` | 2026-08-26 | `7b068359` | 引入 outcome 分类法 | 未知（未记录） |
| `rwkv-agent-outcome-v2` | 2026-08-28 | `e0047792` | 未知（提交信息无说明） | 未知（未记录） |

## 备注

- 2026-10-21 的版本改名（wire `g1k` → `agent-wire-v1.0`、考卷 `exam-full` →
  `agent-exam-v1.0`、采样预设 `g1k-agent` → `agent-default`）只换标签，评测行为不变，
  所以 harness 仍是 v22，不加 v23。
