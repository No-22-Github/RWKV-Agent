# BFCL v4 评测分支收口：证据、勘误与迁移边界

日期：2026-08-26（Asia/Shanghai）
分支：`feat/bfcl-v4-ab`

本文是当前 BFCL 评测分支的结论入口。它统一解释 E8/E9、仓库外
`rwkv-abstention-lab` 复测和旧弃权诊断之间的关系；各运行的详细配置与历史过程仍以
[`bfcl-v4-run-log.md`](bfcl-v4-run-log.md) 及对应专项报告为准。

## 1. 结论分层

| 证据 | 可以说明 | 不能说明 |
| --- | --- | --- |
| E8 wrapped Qwen baseline/enhanced | 同一 wrapped/anchor 系统内，增强档的完整系统观测差异 | 公开 Qwen 能力、纯 Harness 因果量或官方 leaderboard 对齐 |
| E9 native Qwen | 原生 FC turn seam、执行器和官方 partial evaluator 已形成可运行闭环 | 已复现官方 50.5%，或 thinking 的独立因果增益 |
| `rwkv-abstention-lab` | 固定 7.2b、固定 prompt 字节和本轮贪心配置下的输出偏好与逃逸出口 | 13.3b 默认值、产品路由协议结论或公开 BFCL 成绩 |
| E3 `finish_task` | 改变工具表后，显式语义出口在负样本上可被模型选择 | E1/E2 的 Harness 增量，或产品必须增加 stop tool |

所有 BFCL 分数都必须同时带上 transport、renderer/anchor、parser、分母和 evaluator
口径。lab 行为分类器、官方 partial evaluator、条件完成样本和公开榜单不是同一种分数。

## 2. E8：有效的同系统 A/B，不是模型榜单

`multi_turn_base` 全 200 题中：

| 档位 | 官方 partial score | 模型调用 | 主要边界 |
| --- | ---: | ---: | --- |
| Qwen wrapped baseline | 38/200 = 19.00% | 2639 | object anchor、`finish_task`、wrapped continuation |
| Qwen wrapped enhanced | 57/200 = 28.50% | 3599 | 同上，另含 1170 次 route 调用及兼容/救援策略 |

观测差值为 +19 题、+9.50 pp。增强档把许多失败从空轮/解析终止推进到了实际执行，
但状态不匹配和执行返回不匹配反而增加。因此这证明的是“完整增强系统在这 200 题上更好”，
不是“规划问题已解决”，也不能把 +9.50 pp 全部归因给某一个 Harness 功能。

RWKV wrapped baseline 为 9/200 = 4.50%。enhanced 路由两次运行都无法形成稳定的
`<route>` 协议输出，因此不报告有效分数；0% 的首次运行只保留为无效诊断。

## 3. E9：主分母改为 60，停止 reasoning 因果归因

E9 使用 Qwen 原生 Chat Completions tools + 结构化 `tool_calls`：

| 档位 | 主结果 | 附加指标 | 解释 |
| --- | ---: | ---: | --- |
| native no-think，全 200 | 47/200 = 23.50% | — | 原生 turn seam 的诊断分 |
| native thinking，预选 60 题 | **18/60 = 30.00%** | 18/51 = 35.29% | 51 只是在剔除 9 个 deadline case 后的条件完成样本 |

thinking 子集中有 9 个 case 出现 `context deadline exceeded`，另有 9 个 case 至少一轮
`finish_reason=length`；两类有 5 个 case 重合。`length` 是模型在既定预算下的收敛失败，
不能按基础设施失败剔除。9 个 deadline 也没有在运行前冻结排除规则，因此头条结果必须保留
原始 60 题分母。

当前 `internal/bfcl/multiturn_native.go` 没有把 `ReasoningContent` 写入可回放历史，后续轮次
只回放 tool calls/results。再加上 no-think 是全 200、thinking 是预选 60，两档既非同一题池，
也非完整同历史协议。因此在修复 reasoning replay 并按冻结题池重跑之前：

- 不报告“thinking +11.8 pp”；
- 不把距离公开 50.5% 的剩余差距归因给 FP8；
- 只把 30.00% 记录为带上述缺陷的诊断结果。

E9 说明原生 FC 路径可以运行并接受官方 partial evaluator 检验；它尚未证明官方校准闭合。

## 4. 旧弃权报告的勘误

[`rwkv-g1i-toolcall-abstention-defect-20260820.md`](rwkv-g1i-toolcall-abstention-defect-20260820.md)
保留为历史诊断，但其核心全称命题已被 2026-08-25 的 7.2b 复测推翻：

> “锚点一旦开启结构，模型必然补完真实工具、无法表达不调用”不成立。

仓库外 `rwkv-abstention-lab` 的关键门禁与结果为：

- 模型：`rwkv7-g1i-7.2b-20260805-ctx16384`；原生续写；贪心近似配置；
- 44,640 条生成记录；prompt SHA-256 反查 3230/3230 匹配；生产 Go parser 33/33 交叉匹配；
- 锚定 + `no_tool` 在官方 partial evaluator 下：`irrelevance` 52.08%；
- 同一配置的正样本：`simple_python` 95.83%、`multiple` 88.33%、`parallel` 85.00%、
  `parallel_multiple` 70.00%；五个已测 split 加权 80.24%；
- 无锚点 + 假思考 + `no_tool` 的负样本虽到 77.08%，但两个 parallel split 都是 0%，
  不能作为工程默认值；
- `arguments` 的对象/字符串形态会被锚点精确空格强烈改变，仍是需要独立处理的数据偏好。

这些数据证明 7.2b 已有部分语义弃权能力，主要问题是出口和格式稳定性；它不证明产品 Harness
应该直接增加 `no_tool`。lab 的 `no_tool` 是 BFCL 单阶段、已预填调用结构中的语义逃逸工具；
产品 Agent 已有独立 route `respond` 和普通 final 出口，必须先在产品协议题库做 A/B。

13.3b 没有进入本轮 lab。旧报告中关于 13.3b 的历史观测没有被本轮复测确认或推翻，不能把
7.2b 的最佳字节、工具名或收益外推成 13.3b 默认值。

## 5. 当前可以保留与迁移的内容

| 内容 | 当前处理 |
| --- | --- |
| BFCL loader/renderer/parser/sidecar/官方评分适配 | 留在评测分支和归档，不整套合入 `main` |
| `ef8b99a` route parser 容忍前置散文/think | 保留为真实 parser 修复；收益需产品题库复测 |
| route prompt framing 不变量与 golden | 做成 focused Harness 修复，可精选迁移 |
| E8/E9 报告和本收口说明 | 可精选迁移为项目证据文档 |
| BFCL irrelevance、缺参追问、多轮决策形状 | 转换成产品 eval case 后再迁移 |
| BFCL JSON anchor、`finish_task`、`no_tool` | 不直接进入产品协议；先做单因子 A/B |
| wire-compat parser | 只记录可恢复量；不能把 repaired 输出算作原始协议成功 |

## 6. 归档与发布状态

当前已提交的 E8 小型机器可读归档位于
[`archive/bfcl-v4-e8-qwen-enhanced-base-20260822/`](../../archive/bfcl-v4-e8-qwen-enhanced-base-20260822/)。
仓库外完整 run 和 `rwkv-abstention-lab` 仍以各自 manifest、路径和 SHA-256 清单保存。

分支 push、annotated archive tag 以及回到 `main` 都是后续显式发布步骤；本文完成并不代表这些
远端动作已经执行。正式引用某个 run 时仍须检查其源码 commit、`repo_dirty`、binary hash、
manifest 和原始/归档哈希是否一致。

## 7. 收口后的下一步

1. 先让正式 Agent eval 区分主动 `respond`、普通 final、route fail-closed、tool-like parse
   failure 和 Harness repair。
2. 再用 schema-only trap tools 导入 BFCL `irrelevance`，分别跑 router-off decision suite 与
   router-on route suite。
3. 加入“缺 required 参数应追问 / 补齐后应调用”的成对题。
4. 每个 Harness 行为改动单独 A/B；保留正样本、解析有效率、延迟和调用成本护栏。

在这些产品协议证据出现前，lab 的最佳输出偏好只作为候选因子，不作为新的产品默认行为。
