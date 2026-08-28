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

## 后续扩展

先用这 60 题建立产品协议基线，再按失败分布增加题目。扩展仍应保持独立题库、正反配对和单因子 A/B；BFCL 的 `finish_task`、anchor 字节和官方判分逻辑不直接进入产品默认协议。`no_tool` 只作为默认关闭、可追踪、文本续写限定的产品实验开关，不能用 BFCL 结果直接证明默认产品增益。
