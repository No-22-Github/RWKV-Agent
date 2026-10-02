# 正式版 G1K 格式消融（无 state）— 预注册计划

日期：2026-10-03。分支 `exp/g1k-official-format`。

## 要回答的问题

正式版 `rwkv7-g1k-7.2b-20260930-ctx25600` 不借助 state，换 harness 线路格式能否比现行 `--profile g1k` 提分；
哪种格式最贴合它的输出习惯，v1.3 语料要不要按这种格式重新渲染。

## 动机（smoke 10 题，2026-10-03）

- 10/10 题第一步自发写 `<think>…</think>`（中文），g1k 是 thinking=off，think 块使该步协议无效、需要重试。
- 5/10 第一步用 OpenAI 风格 `<tool_calls>[{"function":{…},"type":"function"}]`；另有 `<tool_call>\n{json}\n` 的
  Hermes/Qwen 换行写法——训练语料是无换行的 `<tool_call>{json}</tool_call>`。
- 7/10 以 `no_tool(reason=答案)` 收尾。

## 设置

- 端点：直连网关 `http://100.64.0.4:8018/v1`（NO_PROXY），总并发 64，`bench sweep` 前后快照。
- 采样：`g1k-agent`（T0.3/top_p0.5）。预算按规程：16 步、4096/2048 token、单题 30 分钟、合并窗口 0。
- 套件：workbank（148，**主口径为去掉 seeded-base700 的干净 112**）、bfcl-product 60（中文 40 / 英文 irrelevance 20 分开报）。
- 闸门：`bench sweep` 内置 `run check`，格式消融时校验 `wire_profile == --profile`（本分支新增）。

## 各组

阶段 1（现成修饰项，k=0）：

| 组 | --profile | 假设 |
|---|---|---|
| A | `g1k` | 基线 |
| B | `g1k+think-fast` | 预填空思考块，堵住自发思考 |
| C | `g1k+think-full` | 放开思考，按思考模式解析 |
| D | `g1k+fake-think-closed` | 预填已闭合思考块（与 B 的差别在闭合方式） |

阶段 2（本分支实现）：Hermes 风格线路（System 用 Hermes 措辞与 OpenAI function schema 工具清单、
`<tool_call>` 标签内换行、`<tool_response>` 包装、解析器接受 `<tool_calls>` 数组），配阶段 1 最好的思考设置。

## 判定规则

1. 阶段 1、2 每组 k=1 筛选；排名用 workbank 干净 112 + bfcl-product 60 的 strict 正确数之和。
2. 前两名（含基线）补到 k=3；差距小于同组 k 次极差记为「无法区分」，此时选改动更少的格式。
3. 报配对翻转与符号检验；失分用 `run gate` 分层，区分协议/收尾/能力。
4. 选出的格式若不是 g1k，v1.3 语料需按它重新渲染（wire_hash 会变），训练中的 state 只能在 g1k 下评测。
