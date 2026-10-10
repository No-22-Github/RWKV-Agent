# 正式版 G1K 格式消融（无 state）— 报告

日期：2026-10-03。分支 `exp/g1k-official-format`。计划见 [PLAN.md](PLAN.md)，汇总脚本 [summarize.py](summarize.py)。

## 0. 结论

1. **现行 `--profile g1k` 仍是最稳的基线**：workbank 干净 112 题 5–6，bfcl-product 45–48/60（中文 34–36/40）。
   正式版在 g1k 下比 temp-3601 基模（9/112、40/60）bfcl 高 5–8 题、workbank 低 3–4 题；workbank 的单 run 极差未测，差距可能在噪声内。
2. **放开思考（`g1k+think-full`）workbank 最高（9/112，148 全量 12），但 bfcl irrelevance 从 11–12/20 掉到 4/20**：
   思考后更倾向调工具，不该调时也调。合计 41 低于 g1k 的 51–53。
3. **Hermes Agent 轨迹格式（`align=hermes`）不可用**：四个变体 workbank 全部 0/148，bfcl-product 14–21/60。
   原因是模型在这个格式下拿到工具结果后从不转去写文字答案，而是继续调工具（计算器算出 9000 后再用 `"9000"` 调计算器），
   直到重复被拒、强制收尾，收尾阶段仍在调（`closeout_tool_call` 53–62/112）。工具结果放 `User:` 回合还是 `Tool:` 行、
   去不去掉 harness 提醒，都不改变这一模式。正式版大概率不是直接用 Hermes 轨迹训的；它自发写出的
   `/home/node/.openclaw/workspace` 路径指向 OpenClaw 一类数据。
4. **预填空思考块（`think-fast`）不提分**：零调用直答 42→13、收尾吐调用 28→13，但答错 6→21、整句作答/拒答 4→20，总分持平略低。
5. harness 层修复（本分支）：OpenClaw 风格绝对路径映射、空 `no_tool` 答题阶段的 `Assistant: Assistant:` 重复标签、
   G1 解析器接受字符串化 `arguments`。g1k 对照（pA，新二进制）比 fA（旧二进制）bfcl +3、workbank −1，单 run 内无法区分。

6. **解析恢复（`recover-json`）把零调用直答从 42 压到 15，但捞回的调用全部转成「收尾阶段吐工具调用」**（rJ 49/112），
   总分不涨（rJ 4、rCJ 7）。瓶颈不是不会调工具，而是**调完不会收尾作答**——换格式、改解析都绕不过去，
   正是 v1.3 语料 N10 收尾恢复样本要训的行为。

**对 v1.3 的含义**：训练语料的 g1k 格式不需要改，按原计划用 g1k 评测 state。无 state 的最好配置是
`g1k+think-full`（workbank 8–9/112，三次 7–9），代价是 bfcl 中文 −5~7；产品默认仍建议 `g1k`。

## 1. 设置

| 项 | 值 |
|---|---|
| 模型 | `rwkv7-g1k-7.2b-20260930-ctx25600`，engine `albatross-1.3.0`，hard_max_bsz 169（每次 sweep 前后快照在 `local/runs/bench-20261003-fmt/endpoint-*`，全程未变） |
| 端点 | 直连网关 `http://100.64.0.4:8018/v1`，总并发 64 |
| 采样 | `g1k-agent`（T0.3 / top_p0.5），k=1 |
| 预算 | 16 步、answer 4096 / decision 2048 token、单题 30 分钟、合并窗口 0 |
| 套件 | workbank 148（主口径干净 112，去掉 `seeded-base700.txt`）、bfcl-product 60 |
| 二进制 | 阶段 1 `2f012859`（55c62a2 起的分支首版）；阶段 2 `976bd6e8`（ec84b51）；阶段 3 `77141825`（1c0f17d）；阶段 4 `994d5cbf`（ac721e4） |
| 闸门 | 每个 run 过 `run check`（格式消融时校验 `wire_profile == --profile`，本分支新增），invalid 0、infra_errors 0 |

## 2. 结果（strict，k=1）

| 组 | --profile | 二进制 | wb 干净 112 | wb 148 | bfclp | 中文 40 | irrel 20 | 合计 |
|---|---|---|---|---|---|---|---|---|
| fA | `g1k` | 阶段 1 | 6 | 6 | 45 | 34 | 11 | 51 |
| fB | `g1k+think-fast` | 阶段 1 | 5 | 5 | 41 | 27 | 14 | 46 |
| fC | `g1k+think-full` | 阶段 1 | **9** | **12** | 32 | 28 | 4 | 41 |
| fD | `g1k+fake-think-closed` | 阶段 1 | — | — | — | — | — | 校验拒绝：该预填只支持 md-fence |
| pA | `g1k` | 阶段 2 | 5 | 5 | **48** | **36** | 12 | **53** |
| pH | `g1k+hermes+hermes-think` | 阶段 2 | 0 | 0 | 21 | 15 | 6 | 21 |
| pN | `…+no-abstain` | 阶段 2 | 0 | 0 | 14 | 10 | 4 | 14 |
| pD | `…+no-abstain+dup-continue` | 阶段 2 | 0 | 0 | 6 | 1 | 5 | 6 |
| pT | `g1k+hermes+hermes-think+no-nudge+tool-role` | 阶段 3 | 0 | 0 | 20 | 15 | 5 | 20 |
| pTD | `…+dup-continue` | 阶段 3 | — | — | — | — | — | 第 1 次 40 分钟判基础设施错误，第 2 次随后台任务超时被杀，作废 |

## 3. workbank 干净 112 失分分类（classify_failures.py）

| 类 | fA | fB | fC | pA | pH | pT |
|---|---|---|---|---|---|---|
| 零调用直答 | 42 | 13 | 41 | 42 | 6 | 10 |
| 收尾阶段吐工具调用 | 28 | 13 | 3 | 40 | 53 | 61 |
| 其他协议错误 | 14 | 26 | 3 | 7 | 12 | 7 |
| 思考块未闭合 | 7 | 0 | 15 | 8 | 0 | 0 |
| 答错 | 6 | 21 | 18 | 5 | 13 | 13 |
| 整句作答/拒答 | 4 | 20 | 15 | 3 | 10 | 7 |
| 通过 | 6 | 5 | 9 | 5 | 0 | 0 |

## 4. 观察到的正式版输出习惯

- g1k（thinking=off）下 10/10 smoke 题第一步自发写中文 `<think>…</think>`；System 里的「Do not emit <think>」不起作用。
- 工具调用常用 `<tool_call>\n{json}\n` 的 Hermes/Qwen 换行写法，或 OpenAI 风格 `<tool_calls>[{"function":{…},"type":"function"}]`。
- 绝对路径：`/home/node/.openclaw/workspace`（10 次，OpenClaw 默认工作区）、`/workspace/…`、`/app/…`。
- 编造 Hermes Agent 的工具名与字段：`search_files`、`read_file` 的 `lines`/`start_line`、`web_fetch` 的 `url`。
- 收尾阶段几乎必吐工具调用（fA 答题阶段 95 次生成里 89 次是 `<tool_call>`）。

## 5. 本分支的 harness 改动

| 提交 | 改动 |
|---|---|
| c0a1c1f / 4bb8b46 | `align=hermes`（Hermes Agent `_TRAJECTORY_SYSTEM_PROMPT`、每轮 `<think>\n</think>\n`、`<tool_response>` 带 `tool_call_id/name/content`）、`prefill=hermes-think`；`bench sweep --profile`、`run check --profile` |
| bb5210d | 绝对路径取最后一个 `workspace` 段之后的部分；修饰项 `dup-continue` |
| 39e6907 | `RWKVChatRenderer` 不再拼出 `Assistant: Assistant:`；修饰项 `no-abstain` |
| 1c0f17d | 实验开关 `toolrole=tool`、修饰项 `no-nudge` / `tool-role` |
| ac721e4 | G1 解析器接受字符串化 `arguments` |

## 6. 阶段 5（二进制 58f6c36，解析恢复）

| 组 | --profile | wb 干净 112 | wb 148 | bfclp | 中文 40 | irrel 20 | 合计 |
|---|---|---|---|---|---|---|---|
| rJ | `g1k+recover-json` | 4 | 4 | 45 | 30 | 15 | 49 |
| rCJ | `g1k+think-full+recover-json` | 7 | 11 | 38 | 28 | 10 | 45 |

| 类（干净 112） | pA | qC | rJ | rCJ |
|---|---|---|---|---|
| 零调用直答 | 42 | 37 | 15 | 15 |
| 收尾阶段吐工具调用 | 40 | 8 | 49 | 14 |
| 答错 | 5 | 19 | 5 | 29 |
| 通过 | 5 | 8 | 4 | 7 |

## 6.5 未做 / 待定

- 只有 k=1；按 PLAN §2，前两名与基线需补到 k=3 才能下「可区分」结论。
- 阶段 4（`g1k+dup-continue`、`g1k+think-full` 新二进制复测）见 §7。
- train-1-3 的 checkpoint 在训练机上，本机拿不到（约定不 ssh）；拷回后运行 `bench/distill/tools/test-1-3.sh <目录>`。

## 7. 阶段 4（二进制 ac721e4）

| 组 | --profile | wb 干净 112 | wb 148 | bfclp | 中文 40 | irrel 20 | 合计 |
|---|---|---|---|---|---|---|---|
| qD | `g1k+dup-continue` | 5 | 5 | 43 | 31 | 12 | 48 |
| qC | `g1k+think-full` | 8 | 10 | 41 | 29 | 12 | 49 |

- **dup-continue**：收尾阶段吐调用 40→0，但重复后继续调用陷入循环，协议错误 7→40、平均调用 2.3→6.6，总分不涨。
- **think-full 复测**：workbank 8/112（fC 为 9），两次都比 g1k（6、5）高约 3 题；bfcl irrelevance 这次 12/20（fC 只有 4/20），
  说明 fC 的 irrelevance 暴跌大半是单次噪声。中文 40 题两次 28/29，比 g1k 的 34/36 低 5–7 题，这一项两次一致。
- g1k 系所有变体最大的失分项都是「零调用直答」（37–42/112）。细看其中不少是协议垃圾而非真的直答：
  「说明文字 + `<tool_call>`」整段被当成终答（`Never mix commentary with a tool call` 的严格解析），
  以及极少数疑似续写系统提示的输出（如 `, and content=\"full\"}}\n</tools>`、`' way to answer directly. Never invent fi'`），
  每 run 0–2 次（约 0.3% 的生成），可能是推理引擎 `albatross-1.3.0` 的提示截断或缓存问题，留给推理侧排查。
