# BFCL v4 产品语义迁移 suite

日期：2026-08-26（Asia/Shanghai）；2026-08-28 更新产品 profile 与 terminal rationale A/B

## 范围

主线新增内置 suite `bfcl-product`，共 60 题。它是产品 Harness 的语义回归集，不是 BFCL 官方成绩，也不加载 BFCL evaluator、JSON anchor 或原始函数目录。

从 Run schema v6 起，这个 suite 强制使用与 App 共用的 `ProductHarnessOptions`：
`rwkv-g1i-functions-product-v1` + `rwkv-g1i-functions-product-continuation-v1`，默认开启
`rwkv-g1i-tool-route-v1`。Primitive 的 `submit`、BFCL wrapped anchor 和 XML 兼容协议不进入
该 profile。

| 分组 | 数量 | 来源与目的 |
| --- | ---: | --- |
| `bfcl-irrelevance` | 20 | 冻结 BFCL v4 `irrelevance` 原题，保留原题文和题目 ID，只验证产品工具目录下的主动不调用 |
| `bfcl-missing-required` | 20 | 10 组缺参/已给参配对；来源标注 BFCL `simple_python` 题 ID，映射到 `read_file`/`search_text` |
| `bfcl-multiturn` | 20 | 10 组状态推进/失败恢复配对；来源标注 BFCL `multi_turn` 题 ID，映射到产品只读工作区 |

BFCL 数据来源固定为 `6ea57973c7a6097fd7c5915698c54c17c5b1b6c8`。后两组不是把 BFCL 函数名硬塞进产品，而是保留“缺少必要信息”“提供信息后执行”“失败后恢复”“已获得证据后终止调用”这些可迁移语义。

## 运行

```sh
./dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite bfcl-product \
  --output runs/local-bfcl-product
```

可用 `--case bfcl_irrelevance_...` 重跑单题或一组题。suite 的 `summary.json` 应重点查看 `task_success`、`active_no_call`、`no_call_accuracy`、`tool_selection`、`argument_accuracy` 和多轮逐题失败原因；不要把它们汇总成 BFCL leaderboard 分数。当前 suite 用 `Tools`/`Calls` 表达精确调用预期，所以 `required_tool_completion` 与 `required_call_accuracy` 为 0/0 是 schema 语义，不是漏跑。

两个模型偏好实验默认关闭，可单因子或组合运行：

```sh
./dist/rwkv-cli agent-eval \
  --model /absolute/path/to/rwkv7-model.pth \
  --suite bfcl-product \
  --semantic-no-tool \
  --decision-fake-think \
  --output runs/local-bfcl-product-no-tool-fake-think
```

`--semantic-no-tool` 是文本协议伪动作，不执行工具、不伪造 evidence，并单独记录
`semantic_no_call`。`--decision-fake-think` 只作用于 unanchored inspect decision；已有 JSON
fence/object/array anchor、answer stage 和 native function calling 均不使用。显式设置
`--progressive-tools=false` 是无 Router 校准，此时 route accuracy 为 0/0，不得和默认产品
Router 运行混报。

## 7B live Product P0 A/B（2026-08-27 至 2026-08-28）

### 严格空参数版（历史结果，已被 terminal rationale 修订）

运行对象是 `rwkv7-g1i-7.2b-20260805-ctx16384`，经 `/v1/batch/completions`
原生续写；`top_k=1`，服务端 stop token 为 `0,261,24281`，每组 60 题、
`case_parallelism=40`。四组共享 schema v6、`rwkv-agent-eval-v20`、
`rwkv-agent-outcome-v2` 和同一组 case ID。这里是模型加 Product Harness 的自定义回归，
不是官方 BFCL 分数。

首轮产物：

| cell | 开关 | task success | answer | route | tool selection | arguments | active no-call | decision protocol | 模型传输错误 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 均关闭 | 12/60 | 11/41 | 42/61 | 12/61 | 20/31 | 12/30 | 212/230 | 0 |
| semantic | `semantic-no-tool` | 12/60 | 12/44 | 42/64 | 23/64 | 16/34 | 12/30 | 151/189 | 0 |
| fake-think | `decision-fake-think` | 17/60 | 22/45 | 47/65 | 22/65 | 21/30 | 17/35 | 191/207 | 0 |
| combined | 两者均开 | 14/60 | 18/44 | 44/64 | 25/64 | 15/31 | 14/33 | 130/156 | 2 个 HTTP 524 |

确认复跑只保留 baseline、fake-think、combined，总并发 120：baseline 再次是
12/60，且通过的 12 个 case 与首轮完全相同；fake-think 再次是 17/60，相对同轮
baseline 仍为 `+5/-0`，但复跑有 3 个 HTTP 524，因此干净的 fake-think 主结果取首轮；
combined 在无传输错误的复跑为 19/60、相对 baseline `+7/-0`，但跨跑从 14/60
波动到 19/60，不能据此升为默认。

分层结果比总分更重要：两轮 baseline/fake-think 都是 `bfcl-irrelevance` 2/20、
`bfcl-missing-required` 10/20；fake-think 的 5 个净增全部来自 `bfcl-multiturn`
state case。也就是说，这个开关改善的是 unanchored inspect decision 后的状态推进，
没有改善本套题里的 irrelevance 拒调。

旧版 `semantic-no-tool` 单开没有翻转任何 case。它记录了 9 个 `semantic_no_call`，同时产生
17 个 `tool_shape_invalid`；失败输出大量是 `arguments.reason` 或 `arguments.answer`，而
当时协议只接受精确空对象。这与 7B 输出习惯实验的结论一致：从 `{"name":"`
自由续写时，模型倾向追加解释参数。这个结果现在只作为旧严格 parser 的历史基线，不再
代表当前 `semantic-no-tool` 语义。

旧版结论是两个开关继续默认关闭；`decision-fake-think` 有重复增益，而只接受空参数的
`semantic-no-tool` 仅有诊断价值。下面的修订实验改变了后者的 parser 与终止语义，但没有
改写或删除这组历史产物。

### Terminal rationale 修订（2026-08-28）

7B 自然生成的 `reason` / `answer` 不是无意义的“多余字段”，而是适合反馈给用户的模型解释。
修订后的 parser 只放行可选字符串 `reason` / `answer`，不接受任意参数；`answer` 优先，否则
`reason` 直接终止该轮并成为用户可见回复。原始动作和解释保留在 trace / App 事件中，但始终
保持 `toolExecuted=false`、`toolEvidence=false`。空参数仅保留旧二阶段兼容路径。

以同一干净 baseline（`case_parallelism=30`）作成对参照，并用 `case_parallelism=10` 各跑
一组 terminal 60 题；三组均无模型传输错误：

| cell | 开关 | task success | answer | route | tool selection | arguments | active no-call | protocol | stage contract | model calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 均关闭 | 12/60 | 11/41 | 42/61 | 12/61 | 21/31 | 12/30 | 234/297 | 236/297 | 359 |
| terminal semantic | `semantic-no-tool` | 25/60 | 42/60 | 54/80 | 37/80 | 19/40 | 23/40 | 183/216 | 198/216 | 305 |
| terminal combined | 两者均开 | 23/60 | 41/60 | 52/80 | 33/80 | 15/40 | 22/40 | 164/199 | 180/199 | 289 |

terminal semantic 相对 baseline 是 `+13/-0`，成对 exact McNemar 双侧 `p=0.000244`；净增是
全部 10 个 `bfcl-multiturn` state case，以及 `bfcl_supplied_simple_python_1`、`14`、`35`。
terminal combined 为 `+11/-0`、`p=0.000977`，净增是同一组 10 个 state case 和
`bfcl_supplied_simple_python_1`。分层结果为 baseline `2/20, 10/20, 0/20`，terminal semantic
`2/20, 13/20, 10/20`，terminal combined `2/20, 11/20, 10/20`（依次为 irrelevance、
missing-required、multiturn）。因此这里的增益是模型用解释性 no-call 结束中间状态、减少重复
生成；irrelevance 始终是 2/20，不能宣称一般拒调能力提高。

combined 没有在 semantic 之上增加通过 case，反而少通过 supplied `14`、`35`；因此在这 60 题
的最终 prompt 上，fake-think 没有额外任务收益。两开关仍默认关闭：这是单一 7B checkpoint
的产品回归，不足以直接改变默认协议；但 `semantic-no-tool` 已从“只认空对象的诊断开关”修订
为保留用户可见解释、执行边界严格、可继续扩样本验证的实验能力。两组最终 run 均无 model
transport error。中间一组并发 30 的 semantic run 出现 16 个 HTTP 524，已从主结论排除；
更早一组仍提示“下一次续写再回答”的 terminal run 为 23/60、23/60，也因 prompt 字节已被
最终语义替换而不作为主结果。

### 锚点深度 × 语义出口 2×2（2026-08-28，默认值已据此变更）

在 `api-7b.rwkvos.com`（`rwkv7-g1i-7.2b-20260805-ctx16384`）上跑同一 60 题，
`case_parallelism=8`，`--api-stop-tokens cuda`。baseline 复现前一节的 12/60，
逐题一致，因此四格可比。

| cell | 开关 | task success | irrelevance | missing-req | multiturn | protocol repaired | model calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 均关闭 | 12/60 | 2/20 | 10/20 | 0/20 | 17/218 (7.8%) | 358 |
| semantic | `semantic-no-tool` | 23/60 | 2/20 | 11/20 | 10/20 | 12/131 (9.2%) | 313 |
| deep-anchor | `deep-tool-anchor` | 12/60 | 2/20 | 10/20 | 0/20 | 6/211 (2.8%) | 355 |
| **deep-semantic** | 两者均开 | **24/60** | 2/20 | 12/20 | 10/20 | **0/131 (0.0%)** | 316 |

成对 exact McNemar 对 baseline：semantic `+11/-0` `p=0.000977`；deep-anchor
`+0/-0` `p=1.000000`；deep-semantic `+12/-0` `p=0.000488`。deep-semantic 对
semantic 是 `+1/-0`（多过 `bfcl_supplied_simple_python_35`），落在噪声内。

两个开关正交，各自负责不同的东西：

- `semantic-no-tool` 改任务能力。净增逐题都是 10 个 `bfcl_state_multi_turn_base_*`
  加 `bfcl_supplied_simple_python_1`，与前一节记录的增益来源一致。`irrelevance`
  四格恒为 2/20，因此收益机制是"用解释性 no-call 收尾中间状态、减少重复生成"，
  **不能宣称一般拒调能力提高**。
- `deep-tool-anchor` 只改格式稳定性。单开逐题 `+0/-0`——通过的是完全同一批题——
  但 protocol repair 率 7.8% → 2.8%，与 semantic 叠加后归零。先前担心的
  "深锚点移除句法弃权出口会拖低 irrelevance"没有出现。

据此把两个开关的产品默认改为开启（`decisionFakeThink` 仍默认关闭，本轮及前一节
都未显示额外任务收益）。开关本身保留，可显式关闭，以便后续在 13.3b 上做同样对照。
仍是单一 7B checkpoint、单次运行、60 题的结果；`irrelevance` 在四格中无区分度，
说明该题库在拒调维度上测不动，需要另行扩样本。

### XML 与 markdown 两个产品 transcript 对照（2026-08-28）

`no_tool` 已在 XML 信封中实现，参数校验和 Runner 语义与产品 profile 完全共用，因此
`--suite bfcl-product` 同时接受两种 transcript，可在同一批 60 题上直接对照。同一端点、
同一 `--api-stop-tokens cuda`、`case_parallelism=8`。

| cell | task | answer | tool sel | arguments | protocol | stage | route |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| md-baseline | 12/60 | 11/41 | 12/61 | 21/31 | 235/296 | 237/296 | 42/61 |
| md-semantic | 23/60 | 42/60 | 34/80 | 17/40 | 190/224 | 205/224 | 53/80 |
| md-deep-semantic（当前默认） | **24/60** | 41/60 | 34/80 | 22/40 | 192/224 | 208/224 | 52/80 |
| xml-baseline | 21/60 | 39/60 | 42/80 | **34/40** | **236/240** | **236/236** | 62/80 |
| xml-semantic | 20/60 | 34/60 | 43/80 | 31/40 | 225/228 | 225/225 | 61/80 |
| xml-fast（`--thinking fast`） | 21/60 | **46/60** | 41/80 | 33/40 | 228/236 | 228/228 | **62/80** |
| xml-full（`--thinking full`） | 15/60 | 28/59 | 50/79 | 24/39 | 109/161 | 109/109 | 61/79 |

结论分三条：

- **task success 上 markdown 领先 3 题（24 vs 21），但 `+0/-3`、`p=0.25`，未达显著。**
  其余每项 XML 都赢，且差距更大：参数正确率 85% 对 55%，stage contract 100% 对 93%，
  protocol validity 98% 对 86%。失败模式不同——XML 是"该停时没停"（多调工具），
  markdown 是格式错。
- **`no_tool` 在 XML 上 0 次触发**（markdown 44 次）。该 transcript 默认出口本就是直接
  输出普通文本，不像 fenced JSON 开了围栏就必须补完调用，因此语义出口没有用武之地。
  据此 XML 上该开关默认关闭，显式开启仍生效。
- **`--thinking full` 显著有害**：`+0/-6`、`p=0.0312`，protocol validity 塌到 68%——完整
  推理撑爆 decision 预算，think 块未闭合即被截断。`--thinking fast` 在 task 上持平
  （`+1/-1`），但 answer accuracy 39/60 → 46/60 为全场最高，作用在答案表达而非工具决策。

### 失败归因：瓶颈在路由层，不在动作协议（2026-08-28）

对 xml-baseline 的 39 道失败题逐条分类后，最大一块与协议选择无关：

| 分组 | 失败数 | 主要形态 |
| --- | ---: | --- |
| `bfcl-irrelevance` | 18/20 | 路由判成 `inspect`，随后被迫调用工具 |
| `bfcl-multiturn`（recovery） | 10/10 | 工具序列错 + 答案内容错 |
| `bfcl-missing-required` | 9/20 | 选错工具（`want search_text` 却调 `read_file`/`list_files`） |

irrelevance 那 18 题的机制是：路由把纯知识题判成 `inspect`，模型于是被迫进入工具循环
并越挖越深（实测有连续三次 `list_files` 递增 `max_depth`），最终答案其实算对了，但
`active no-call required` 与 `tools want []` 两项检查失败而整题判负。

关键在于 **xml-baseline 与 md-deep-semantic 在这 20 题上都是 18/20 路由错判，完全相同**。
路由是动作协议之前的一次独立短生成（`rwkv-g1i-tool-route-v1`，48 token），两个 profile
共用同一 renderer 与同一段 prompt，因此这 18 题的成败与选哪个动作协议无关——这也解释了
为什么全部七格的 irrelevance 恒为 2/20。

推论：该题库在拒调维度上测不动，不是题目问题，而是瓶颈位于路由层，动作协议改动无法触及。
后续优化的杠杆在路由 prompt 本身（它当前的 `respond` 示例只覆盖"写代码/解释概念"，未覆盖
"解方程"这类纯计算题），而不是继续调协议或停止策略。

### 决策预算是 transcript 的属性，不是全局常量（2026-08-28）

上一节把 irrelevance 恒为 2/20 归因于路由层。关掉路由后复查发现归因只对了一半：
误调用确实从 18/20 降到 1–3/20，但 irrelevance 没涨，17 题改栽在
`answer contract repaired: [protocol_tag]`。逐条查看原文，那些 `<think>` 块**停在句子
中间**——不是模型忘了闭合，是 `decision_max_output_tokens=96` 把它砍断了：

```
...the closest integer to 30 is 30. So answer: 30.
We should respond with            ← 预算耗尽
```

抬高决策预算后（其余配置不变，无路由）：

| cell | task | irrelevance | miss-req | multiturn | answer | arguments | protocol |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| md-deep-semantic（当前默认，96） | 24/60 | 2/20 | 12/20 | 10/20 | 41/60 | 22/40 | 192/224 |
| md-d512（有路由） | 22/60 | 2/20 | 12/20 | 8/20 | 38/59 | 21/39 | 191/226 |
| md-d512-noroute | 20/60 | 10/20 | 10/20 | **0/20** | 21/55 | 9/35 | 113/150 |
| xml-noroute（96） | 24/60 | 4/20 | 11/20 | 9/20 | 38/60 | 33/40 | 147/180 |
| **xml-d512** | **33/60** | **12/20** | 12/20 | 9/20 | 42/60 | **34/40** | **184/189** |
| xml-d1024 | 33/60 | 12/20 | 12/20 | 9/20 | 42/60 | 34/40 | 187/191 |
| xml-d512 复现 | 31/60 | — | — | — | — | — | 97.4% |

- `xml-d512` vs `xml-noroute(96)`：`+9/-0`、`p=0.0039`；vs 当前默认：`+10/-1`、`p=0.0117`。
- `xml-d1024` vs `xml-d512`：`+0/-0`，512 已是拐点。
- 同条件（都无路由、都 512）`xml-d512` vs `md-d512-noroute`：**`+16/-3`、`p=0.0044`**。

**96 是为 fenced-JSON 调的值。** 该 profile 预填围栏锚点把模型直接推进调用对象，几乎
不花思考预算；XML 信封让模型先推理再决定，96 天然不够。因此
`decision_max_output_tokens` 改为按 protocol 取默认（markdown 96 / XML 512），此前所有
XML 与 markdown 的对比都是在对 XML 不利的预算下做出的。

注意该值仍受 `Generation.MaxOutputTokens` 夹取，默认答案预算 256 时 XML 实际只能拿到
256；要用满 512 需同时给出足够的 `--max-tokens`。

另一条结论是 markdown 对路由的依赖是结构性的：`md-d512-noroute` 的 irrelevance 从 2/20
升到 10/20，但 multiturn 塌到 0/20，总分反而跌到 20。路由替它筛掉简单题，代价是
irrelevance 上不去。XML 两项都拿得住，不需要这层托底。

同时修复一个客户端缺陷：该后端在 batch 端点恒返回 `finish_reason: "stop"` 且不返回
usage，即使响应被 `max_tokens` 截断（`max_tokens=5` 实测输出停在 `<think>好的` 仍报
stop）。非流式路径此前全盘接受该字段，导致"预算耗尽"被动作协议误诊为"畸形信封"。现改为
在无 usage 时不盲信，与流式路径一致。

### 路由层在 XML 上是净负担（2026-08-28）

把"换协议"和"关路由"拆成两个决策后实测，二者不可分：

| 配置 | task | irrelevance | miss-req | multiturn | irrelevance 被判成 inspect |
| --- | ---: | ---: | ---: | ---: | ---: |
| markdown + 路由（当前默认，96） | 24/60 | 2/20 | 12/20 | 10/20 | 18/20 |
| markdown 无路由 + 512 | 20/60 | 10/20 | 10/20 | **0/20** | — |
| XML + 路由 + 512 | 21/60 | 2/20 | 11/20 | 8/20 | 18/20 |
| **XML 无路由 + 512** | **33/60** | **12/20** | 12/20 | 9/20 | — |

XML 的两格只差路由开关，相差 12 题且几乎全在 irrelevance。因果是明确的：路由在这 20 题上
有 18/20 判成 `inspect`，模型随即被迫进入工具循环——**路由否决了模型本来正确的拒调判断**
（无路由时模型自己拿到 12/20）。因此 XML 的收益必须配合无路由，无法只换协议而保留路由架构。

三次独立复现 XML 无路由 + 512：33 / 31 / 33，均值 32.3、标准差 1.2。对当前默认的成对检验
分别为 `+10/-1`（p=0.0117）、`+11/-4`（p=0.1185）、`+10/-1`（p=0.0117）——三次方向一致。

路由对 markdown 仍有价值：拿掉后它的 multiturn 塌到 0/20。但那是在补 fenced-JSON profile
自身的短板，不是通用收益。若切换默认，需同时接受：失去 `respond` 快速通道（简单对话也进
工具循环，与省下的一次路由调用大致抵消）、App 的"渐进式工具暴露"开关对 XML 失去意义、
`route_accuracy` 变为 0/0 而历史 run 不可直接对比。

### 已排除：fake-think 三变体（2026-08-28）

`--decision-fake-think`（半开 `<think></think`）与新增的 `--closed-fake-think`
（完整 `<think></think>`）在 markdown 上结果几乎相同（均 17/60，protocol 47%），且都比
不做干预更差。token 层面实测 `>` 与 `>{` 均为 1 个 token（`>{` 合并），完整闭合确实切断
该合并路径，但这个差异在 60 题上未改变任何一题。

真正的变量是二者都必须关掉 `deepToolAnchor`——它们抢同一个 assistant prefix 位置。撤掉
围栏后模型漂移到 XML `<tool_call>` 信封，泄漏 15 → 33/37 次，空响应 19 → 85/89 次。这
反过来说明深锚点的作用不止格式：它把模型钉在 fenced JSON 上。

三种变体（不干预 / 半开 / 闭合）已穷尽该方向。压制思考会把误调用从 1/20 推到 19–20/20；
正确方向相反——给模型想完的预算。

## 后续扩展

先用这 60 题建立产品协议基线，再按失败分布增加题目。扩展仍应保持独立题库、正反配对和单因子 A/B；BFCL 的 `finish_task`、anchor 字节和官方判分逻辑不直接进入产品默认协议。`no_tool` 只作为默认关闭、可追踪、文本续写限定的产品实验开关，不能用 BFCL 结果直接证明默认产品增益。
