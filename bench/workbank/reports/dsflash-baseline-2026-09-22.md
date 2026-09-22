# deepseek-flash 摸底（2026-09-22）

> **跑法**：148 题（下架 4 题后的在用集）× 2 轮，`deepseek-flash` 经中转，`--case-parallelism 40`，
> `--max-steps 16 --decision-max-tokens 8192 --max-tokens 4096 --temperature 0.3`，
> `--tool-catalog work-v1`（系统提示词未改）。产物 `runs/workbank/relay-t03-k{0,1}`。

## 1. 结果

```
279/294 = 94.9%        （k0 139/146 = 95.2%，k1 140/148 = 94.6%）
分层  infra 2 · protocol 4 · toolchoice 1 · format 1 · capability 9
判定  可以当能力读数
冻结 40 题  39/40 与 38/40
```

冻结 40 题的读数与 2026-09-21 的 `flash-*` 系列（38–39/40）吻合。

## 2. 一条必须记住的配置结论：这个模型不能用 temperature 0

本轮先用 `--temperature 0` 跑了一遍（沿用本地 9B/27B 的参数），只有 **109/148 = 73.6%**，
且出现大量「UNKNOWN 早退」（18 题）与「不调 web_search」（12/16 题）。换成 T=0.3 后
UNKNOWN 早退降到 1–2 题、web 检索率升到 15–16/16，**同一套系统提示词、同一个模型、同一批题**。

2026-09-21 的 sweep 早已测出同一结论，证据在 `runs/workbank/flash-greedy-k*`：

| 温度 | 结果 |
|---|---|
| T=0（greedy）5 轮 | 25/40、12/40、8/40、5/40、0/40；作废 14→28→31→33→**40** |
| T=0.01 | 37–39/40，作废 0–2 |
| T=0.3 | 37–39/40，作废 0–1 |

**教训**：给一个没跑过的端点/模型定参数前，先翻 `runs/` 看它跑过什么。本轮因为直接套用本地端点的
`--temperature 0`，在坏配置上做了一整轮关于「系统提示词压制检索」的分析，结论全部作废
（那些现象是温度 0 的伪影，不是提示词的问题）。

## 3. 13 道失败逐题

两轮中至少挂或废过一次的 13 道。**真正像「模型不会」的只有 2 道，且都是 1 过 1 挂的抖动。**

### 判据 / 预算问题（题侧可修，4 道）

| 题 | 两轮 | 实况 |
|---|---|---|
| **web-0002** | 1过1挂 | 答 `45 seconds (as of deltastream 3.0.0; it was 120 in earlier releases).`，**答案正确**，被 `output_equals: "45"` 判挂。这正是审阅报告 S-B 的「`output_equals` 不容出处型补充」——本轮只修了 web-0014/0016，**漏了 web-0002** |
| **web-0014** | 0过2挂 | 答对 `7.4.1`，但 `expect.max_calls: {web_search: 1}` 被 4 次检索判挂。预算是 TR-EARLYHIT 的设计，但拿正确答案去撞预算，值得复核 budget=1 是否过紧 |
| **code-0008** | 1过1挂 | 输出停在 `The actual code is:` ——正要贴代码被截断；且它写的 `only *claims* to reject repeat references` 是正确诊断，判据词表仍未覆盖 "claims" |
| **web-0005** | 1过1挂 | `required tool "web_search" was not called` + UNKNOWN。抖动项 |

### 步数预算不足（script 家族，3 道）

三道都是 `tool_calls` 13–15（上限 16）且 `forced_answers: 1`，即**被强制收尾**：

| 题 | 两轮 | 实况 |
|---|---|---|
| **scr-0016** | 0过2挂 | 13–15 次调用全部用于读 spool 结构，**始终没写成文件**，stub 原样留着（`tally.py: nightly lot rollup not implemented`）。模型自己说 "I could not write or run anything further — the tool session is closed" |
| **scr-0012** | 1过1挂 | 脚本写到一半被截断：`File ".../billing_summary.py", line 21: BASE = Pat` |
| **scr-0020** | 1过1挂 | 同样半截：`line 109 writer.writerow((key, amount)) IndentationError: unexpected` |

这三道被 `capability_gate` 记进 `capability` 层，**归因不对**——它们不是推理失败，是步数/输出预算耗尽在写文件的半路上。
`expect.run` 的报错文案里没有 closeout 标记，分层器看不见。

### 上游协议噪声（2 道，作废）

`scr-0008`、`scr-0009` 各废 1 次：
`function tool call arguments are not a JSON object`——模型发出的 tool_call 参数不是合法 JSON。
`docs/solve-check-20260917.md` 记录过 DeepSeek 的同一毛病，属被测的真实模型行为。

### 输出 token 上限（2 道）

`log-0012`、`nt-0010` 两轮都挂于
`agent protocol error: model response reached the output token limit`，计入 `protocol` 层（4 次）。

### 真能力失败（2 道）

`code-0002`（1过1挂，答 UNKNOWN）、`hyb-0002`（1过1挂，答 UNKNOWN）。
两道都不稳定，样本不足以判定。

## 4. 本轮对题库做的两处改动（已落库）

跑分之前按 T=0 的观察做的，**收益需要按 T=0.3 重新评估**：

- **16 道 web 题加 `expect.required_tools: ["web_search"]`**：这些题没有工作区文件、题面无 URL，
  不检索不可能答出来。T=0.3 下 `toolchoice` 只剩 1 例，说明「没出门」本就罕见，这条现在是**便宜的保险**
  ——真发生时能正确归因而不误记成能力问题。
- **16 道 web 题面补一句「本地没有」的上下文**：T=0.3 下检索率本就 15–16/16，**没有可证明的收益**；
  保留的理由是题面更贴近真实用户会说的话（口径由主控确认）。

`tools/capability_gate.py` 新增 `toolchoice` 层（v1→v2），把「没调必需工具」从 `capability` 层分出来。

## 5. 待办

1. **web-0002 补 `output_equals_any`**（S-B 漏网），**code-0008 词表补 "claims" 类说法**。
2. **复核 web-0014 的 `max_calls: {web_search: 1}`**：答对却因多搜被判挂，两轮皆然。
3. **script 家族的步数预算**：scr-0016 稳定挂在「读完没时间写」。要么提 `--max-steps`，要么承认 16 步是被测能力的一部分——但至少 `capability_gate` 该认出 `forced_answers>0` 并归到 `closeout` 层。
4. **9B 与扩量轮 B1–B5 的闸门读数都是 T=0 下测的**，可能严重低估，值得按 T=0.3 重测。

*报告生成：2026-09-22。*
