# g1k 思考轨迹的形状（2026-10-10）——带思考训练数据的拟合目标

数据：`local/runs/bench-20261010-thinkfull/` 里 T（`g1k+think-full --wire nudge=think`，`g1k-agent`）与 F（同配置、`g1k-agent-fast`）各 3 轮，
workbank 148 + bfcl-product 60，共 4275 个模型步。脚本 [think_shape.py](think_shape.py)（`python3 -I think_shape.py <runs_dir>`，只读），
下方附录是它的原始输出。思考「质量」（有没有在推理、想≠做）见 [think-quality.md](think-quality.md)，本文只描述「长什么样」。

## 0. 结论：训练数据要模仿什么、纠正什么

**模仿（这是 g1k 自己的分布，语料贴着它走，学起来最省）**

| 维度 | g1k 原生形状 | 训练数据目标 |
|---|---|---|
| 标签 | 预填 `<think`，模型补 `>`；`</think>` 后 1 个换行接动作 | 同：`<think>` + 思考 + `</think>\n` + 动作 |
| 长度 | 闭合步中位 200–340 字符（≈60–100 token），p90 500–900 | 每步思考 ≤ 900 字符；首步 250–350、后续步 200–250 为主 |
| 语言 | workbank 100% 英文；bfcl 中文题约 28% 用中文思考 | 英文为主；中文题允许中文思考，不强制 |
| 首步开头 | `The user is asking…` / `The user wants me to…`（>55%） | 先一句复述需求，再说取证计划 |
| 后续步开头 | `The search results are/show…`、`The read_file call failed…` | 先一句总结上一步结果（含具体值），再决定下一步 |
| 收尾句 | `Let me start by…`、`Let me search for…`、`I need to read…` | 以「下一步做什么」收尾，然后马上闭合 |
| 引用结果 | 后续步约 75–80% 提到上一步结果里的新 token | ≥90%：后续步必须引用上一步的具体值/文件名 |
| 工具调用 | `<tool_call>{…}</tool_call>` 紧贴写法约 84–90%，换行写法约 10–16% | 统一紧贴写法（与 g1k 语料契约一致） |

**纠正（g1k 的坏习惯，语料里不能出现，要用正例覆盖）**

| 问题 | 现状（T / F 三轮合计，workbank） | 训练数据做法 |
|---|---|---|
| 写满预算没闭合（复读） | 8.6% / 3.9% 的步 | 过滤；每步思考硬上限 900 字符 |
| 没写 `</think>` 就发调用 | 4.8% / 1.7% | 过滤；所有样本都显式闭合 |
| 终答写成长句/多行 | 309 次只过 7 次 | 终答只给题目要的值（裸值/一个短语），**思考里可以解释，终答不解释** |
| 终答包 `<answer>` | 47 次过 16 次（模型自发，harness 没要求） | 不用 `<answer>`，终答是普通文本 |
| 通过题思考很短 | F 通过题整条轨迹思考中位 613 字符，失败题 1117、p90 17022 | 收集通过轨迹时偏好短的；长思考多半是在打转 |

**一句话**：g1k 已经会用「复述需求 → 计划 → 读结果 → 下一步」的英文短思考，训练数据保持这个形状不变，
只需要把闭合、裸值终答、引用具体结果这三件事做到 100%。老师模型选思考风格接近的（短、英文、电报式），
例如 MiniMax M3/M3.1-Flash（每步 30–300 token）；DeepSeek 长思考（中位 3000+ 字符）需要截短或只取结论段。

## 1. 终答写法与通过率（workbank，T+F 六轮）

| 终答写法 | T（次数 / 通过） | F（次数 / 通过） |
|---|---|---|
| 长句 / 多行 | 160 / 7 | 149 / 0 |
| 裸值 / 短句（≤40 字符） | 74 / 17 | 67 / 16 |
| `<answer>…</answer>` 包裹 | 18 / 5 | 29 / 11 |
| 思考未闭合 | 11 / 0 | 14 / 0 |

## 2. 拟合用的渲染模板（单步）

```text
Assistant: <think>The user wants me to find X in Y. Let me start by listing the logs directory.</think>
<tool_call>{"name":"list_files","arguments":{"path":"logs"}}</tool_call>

User: <tool_response>{…}</tool_response>

User: Use the Tool results above to continue the current task. …（harness 提醒原文，nudge=think 版本）

Assistant: <think>The listing shows logs/checkout-api.log. I need to read it to count ERROR lines on 2026-09-15.</think>
<tool_call>{"name":"read_file","arguments":{"path":"logs/checkout-api.log"}}</tool_call>

…

Assistant: <think>The log has 6 ERROR entries dated 2026-09-15 (14:03:22, 14:32:09, …). The answer is 6.</think>
6
```

- 历史步骤里的思考由 harness 剥掉（每步只看到自己的思考），训练行要按同样形状切行：每行只监督当前这一步的 `<think>…</think>` + 动作。
- 用 `corpus render` 渲染前需要支持 think-full profile（目前只支持 g1k），并锁定新的 wire_hash。

## 附录：think_shape.py 原始输出

## 1. 规模

| 组 | 套件 | 步数 | 闭合 | 闭合率 | 题次 | 通过题次 |
|---|---|---|---|---|---|---|
| F | workbank | 1609 | 1489 | 93% | 448 | 33 |
| F | bfclp | 522 | 497 | 95% | 231 | 162 |
| T | workbank | 1609 | 1351 | 84% | 453 | 34 |
| T | bfclp | 535 | 495 | 93% | 238 | 166 |

## 2. 思考长度（闭合步，字符；p10 / p50 / p90 / max；约 3.5 字符 ≈ 1 token）

| 组 | 套件 | 阶段 | 位置 | 步数 | 通过题 | 失败题 |
|---|---|---|---|---|---|---|
| F | workbank | decision | 首步 | 392 | 174 / 291 / 633 / 1860 | 160 / 334 / 865 / 3183 |
| F | workbank | decision | 后续步 | 957 | 121 / 245 / 516 / 1777 | 89 / 210 / 613 / 8763 |
| F | workbank | answer | 后续步 | 140 | 233 / 754 / 754 / 754 | 167 / 420 / 1434 / 3345 |
| F | bfclp | decision | 首步 | 214 | 40 / 123 / 506 / 1180 | 73 / 129 / 1389 / 2457 |
| F | bfclp | decision | 后续步 | 269 | 98 / 208 / 616 / 2867 | 64 / 207 / 549 / 3009 |
| F | bfclp | answer | 后续步 | 14 | 310 / 312 / 312 / 312 | 243 / 326 / 360 / 421 |
| T | workbank | decision | 首步 | 341 | 153 / 324 / 582 / 782 | 177 / 337 / 842 / 6683 |
| T | workbank | decision | 后续步 | 894 | 98 / 246 / 565 / 4368 | 91 / 191 / 507 / 2128 |
| T | workbank | answer | 后续步 | 116 | 229 / 295 / 1360 / 1360 | 196 / 368 / 899 / 2193 |
| T | bfclp | decision | 首步 | 212 | 41 / 108 / 463 / 1448 | 78 / 173 / 908 / 2376 |
| T | bfclp | decision | 后续步 | 274 | 99 / 204 / 472 / 1343 | 121 / 205 / 464 / 1201 |
| T | bfclp | answer | 后续步 | 9 | 296 / 296 / 296 / 296 | 238 / 358 / 916 / 916 |

## 3. 语言

| 组 | 套件 | 闭合步 | 思考以英文为主 | 思考以中文为主 | 动作/终答含中文 |
|---|---|---|---|---|---|
| F | workbank | 1489 | 1489 | 0 | 0 |
| F | bfclp | 497 | 356 | 141 | 61 |
| T | workbank | 1351 | 1351 | 0 | 0 |
| T | bfclp | 495 | 362 | 133 | 41 |

## 4. F 组：开头与收尾措辞（闭合步，前 4 词）

- 首步开头（n=606）：`The user is asking` 188；`The user wants me` 151；`The user wants to` 24；`We need to answer:` 15；`The user asks: "The` 8；`The user asks for` 6；`Okay, let's see. The` 6；`I need to find` 5
- 后续步开头（n=1380）：`The user wants me` 113；`The user asks for` 80；`The search results are` 69；`The user wants to` 63；`The search did not` 48；`The user wants the` 31；`The read_file call failed` 23；`The search results show` 23
- 收尾句：`Let me start by` 149；`Let me search for` 85；`I need to try` 76；`I need to read` 73；`Let me use the` 38；`I need to search` 36；`Since I cannot determine` 30；`Now I need to` 23
- 输出开头两个字符（`>` 补全标签）：'>T' 1549；'>\n' 325；'>我' 34；'>用' 29

## 4. T 组：开头与收尾措辞（闭合步，前 4 词）

- 首步开头（n=553）：`The user wants me` 171；`The user is asking` 167；`The user wants to` 19；`The user asks for` 11；`We need to answer:` 8；`The user asks: "The` 6；`The user asks: "How` 4；`We need to answer` 4
- 后续步开头（n=1293）：`The user wants me` 104；`The search results are` 103；`The user asks for` 82；`The user wants the` 52；`The search did not` 47；`The user wants to` 43；`The read_file call failed` 35；`The search results show` 28
- 收尾句：`Let me start by` 142；`Let me search for` 93；`I need to search` 84；`I need to read` 62；`I need to try` 57；`Now I need to` 25；`Let me first explore` 23；`Let me first read` 19
- 输出开头两个字符（`>` 补全标签）：'>T' 1500；'>\n' 247；'>我' 39；'>用' 32

## 5. 思考与动作之间的格式

| 组 | 闭合步 | `</think>` 后分隔符 | 工具调用写法 | 终答（无调用）首字符 |
|---|---|---|---|---|
| F | 1986 | '\n' 1889；'' 73；' ' 19 | 紧贴 1309；换行 149 | '<' 139；'I' 115；'T' 108 |
| T | 1846 | '\n' 1761；' ' 43；'' 42 | 紧贴 1119；换行 211 | 'T' 138；'I' 112；'<' 99 |

## 6. 后续步是否引用上一步工具结果（闭合步，position>1）

| 组 | 套件 | 步数 | 引用了结果里的新 token | 通过题内 | 失败题内 |
|---|---|---|---|---|---|
| F | workbank | 1038 | 776/1038 | 32/35 | 744/1003 |
| F | bfclp | 271 | 200/271 | 130/150 | 70/121 |
| T | workbank | 925 | 729/925 | 58/74 | 671/851 |
| T | bfclp | 258 | 214/258 | 140/158 | 74/100 |

## 7. 每题的思考步数与轨迹长度（workbank）

| 组 | 结果 | 题次 | 步数 p50 / p90 | 整条轨迹思考字符 p50 / p90 |
|---|---|---|---|---|
| F | 通过 | 33 | 2 / 3 | 613 / 2829 |
| F | 失败 | 415 | 3 / 8 | 1117 / 17022 |
| T | 通过 | 34 | 2 / 7 | 933 / 22199 |
| T | 失败 | 419 | 3 / 7 | 1120 / 22170 |

## 8. 通过轨迹原文（每组最短的 3 条，workbank，全部闭合）

### F · code-0001 · F-workbank-k0

```text
User: A cardholder-data auditor is walking our senior engineer through the cardholder vault this week and asked where the advisory lock on vault edits is taken. In which file, and on which line, is the function acquire_session_lock defined? Give the location as <relative path>:<line number>. Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.

Assistant: <think>I need to find the location of the function acquire_session_lock in the workspace.
</think>
<tool_call>{"name":"search_text","arguments":{"query":"acquire_session_lock"}}

User: <tool_response>{'ok': True, 'tool': 'search_text', 'result': {'matches': [{'path': 'auth/session.py', 'line': 15, 'text': 'def acquire_session_lock(vault_id, operator):'}, {'path': 'billing/invoice.py', 'line': 5, 'text': 'from auth.session import acquire_session_lock, release_session_lock'}, {'path': 'billing/inv…</tool_response>

Assistant: <think>The search result shows that acquire_session_lock is defined in auth/session.py on line 15. The user asked for the relative path and line number, so I should provide that directly.</think>
<answer>auth/session.py:15</answer>
```

### F · nt-0005 · F-workbank-k0

```text
User: The retention planner for our research data lake needs the nightly archive throughput restated for a capacity sheet. The archive job reads at a steady 1.25 TiB per hour. Give that same rate in TiB per day. Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.

Assistant: <think>The user wants to convert 1.25 TiB per hour to TiB per day.
1 TiB = 24 hours
So, 1.25 TiB/hour * 24 hours/day = 30 TiB/day
I can use the calculator tool for this calculation.</think>
<tool_call>{"name":"calculator","arguments":{"expression":"1.25 * 24"}}

User: <tool_response>{'ok': True, 'tool': 'calculator', 'result': {'expression': '1.25 * 24', 'result': 30, 'formatted': '30'}}</tool_response>

Assistant: <think>The calculator result is 30. The user asked for the archive throughput in TiB per day, given a steady rate of 1.25 TiB per hour. Multiplying 1.25 by 24 gives 30 TiB per day. The answer is complete and exact.</think>
<answer>30</answer>
```

### F · nt-0008 · F-workbank-k2

```text
User: The security questionnaire asks how many hexadecimal characters a SHA-256 digest contains, because the checksum field is sized from that figure. How many hexadecimal characters are in a SHA-256 digest? Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.

Assistant: <think>The user is asking about the number of hexadecimal characters in a SHA-256 digest. I know that SHA-256 produces a 256-bit hash, which is 32 bytes. Each byte is 8 bits, so 32 bytes = 256 bits. In hexadecimal, each bit is represented by 2 characters (0-9, A-F), so 256 bits would be 256 / 8 = 32 bytes, and 32 bytes * 2 = 64 hexadecimal characters.
Let me verify this with the calculator tool to be sure.</think>
<tool_call>{"name":"calculator","arguments":{"expression":"256 / 8 * 2"}}

User: <tool_response>{'ok': True, 'tool': 'calculator', 'result': {'expression': '256 / 8 * 2', 'result': 64, 'formatted': '64'}}</tool_response>

Assistant: <think>The calculator result is 64. SHA-256 produces 256 bits, which is 64 hexadecimal characters. The answer is 64.</think>
<answer>64</answer>
```

### T · nt-0001 · T-workbank-k0

```text
User: A monitoring dashboard reports an ingest rate of 2.5 MiB per second. Express that same rate in MiB per hour. Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.

Assistant: <think>The user wants to convert 2.5 MiB per second to MiB per hour.
1 second = 60 seconds
1 hour = 60 minutes = 3600 seconds
So, 2.5 MiB/s * 3600 s/h = 9000 MiB/h
I can use the calculator tool for this.</think>
<tool_call>{"name":"calculator","arguments":{"expression":"2.5 * 3600"}}

User: <tool_response>{'ok': True, 'tool': 'calculator', 'result': {'expression': '2.5 * 3600', 'result': 9000, 'formatted': '9000'}}</tool_response>

Assistant: <think>The calculator result shows 2.5 MiB per second equals 9000 MiB per hour. That is the final answer.</think>
<answer>9000 MiB per hour</answer>
```

### T · log-0017 · T-workbank-k1

```text
User: ClaimDesk's API writes one plain-text application log per day at logs/claimdesk-api.log. Yesterday a single entry reached FATAL level. For the reliability review, report the module that emitted that FATAL entry. Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.

Assistant: <think>The user wants me to find the module that emitted a FATAL entry in the logs/claimdesk-api.log file. Let me start by reading the file to see what's in it.</think>
<tool_call>
{"name":"read_file","arguments":{"path":"logs/claimdesk-api.log"}}


User: <tool_response>{'ok': True, 'tool': 'read_file', 'result': {'path': 'logs/claimdesk-api.log', 'content': '2025-11-04 09:12:33.412 INFO [claimdesk-api] module=claim-intake msg=claim_registered claim=CLM-40218 channel=broker\n2025-11-04 09:14:07.905 INFO [claimdesk-api] module=document-store msg=blob_written claim=C…</tool_response>

Assistant: <think>The log shows a FATAL entry at 2025-11-04T12:02:33.730Z: "policy-renderer msg=render_worker_exhausted inflight=37 capacity=32 pod=claimdesk-api-7f9c4". The module is policy-renderer. The user asks for the module that emitted that FATAL entry. The answer is policy-renderer.</think>
<answer>policy-renderer</answer>
```

### T · fs-0001 · T-workbank-k1

```text
User: We are moving the finance data room to cold storage and budgeting by file footprint. What is the size in bytes of the largest file in the workspace? Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.

Assistant: <think>The user wants to know the size in bytes of the largest file in the workspace. I need to find all files in the workspace and determine which one is the largest by size.
Let me start by listing the files in the workspace to see what's available.</think>
<tool_calls>
[
{"name":"list_files","arguments":{"max_results":"200","path":"/workspace"}}
]
</tool_calls>


User: <tool_response>{'ok': True, 'tool': 'list_files', 'result': {'entries': [{'path': 'README.md', 'type': 'file', 'size': 280}, {'path': 'exports', 'type': 'directory'}, {'path': 'exports/archive', 'type': 'directory'}, {'path': 'exports/archive/.keep', 'type': 'file'}, {'path': 'exports/chain_wide_totals_2026-08.csv…</tool_response>

Assistant: <think>
The user asks: "What is the size in bytes of the largest file in the workspace?" We have a list of files with sizes: README.md (280), exports/chain_wide_totals_2026-08.csv (497), exports/weekly_sales_2026-06.csv (341), notes/buyer_memo_coffee.md (221), notes/buyer_memo_dairy.md (220). The largest is chain_wide_totals_2026-08.csv at 497 bytes. So answer: 497.
We must reply only with final answer.
</think>
497
```

