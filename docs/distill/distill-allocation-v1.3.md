# 蒸馏数据构成规划 v1.3

> 读者：落地补数据的执行者。流程、命令、闸门仍以 [distill-workflow.md](distill-workflow.md) 为准；本文只规定
> **存量怎么处理、新增加什么、加多少、怎么判**。写于 2026-09-29，基数是 v1.2 mixed
> （`local/outputs/workspace-agent-distill-clean-20260928-v1.2/mixed/rendered/all.jsonl`，1293 行，按行统计）。
> 目标：数据分布从「英文单轮考卷」移向「桌面 Agent 的真实使用」——中文、多轮、失败如实汇报、自然语言交付。
>
> **2026-09-30 修订**：并入 v1.2 横测（[REPORT](../evaluations/state-v12-20260929/REPORT.md)）的逐题轨迹复盘（§1.1）。
> §3 存量修复改为「扫一遍、只修扫出来的」（2026-09-30 扫描结果入库）。新增三条主线：收尾恢复（N10）、UNKNOWN 契约降到少数并规定「查不到 / 做不到」怎么答（§4.1）、工具目录轮换（§4.2）；
> 补 tabular / `data_query`（N11）；前置项加 decontam 中文支持、新管线基线重训、题目级工具子集、lint 认识 answer_style（§2.8–2.13）；验收加 bfcl-product 与失败形态计数（§6）。

## 1. 起点：v1.2 的问题

| 项 | v1.2 | 问题 |
|---|---|---|
| 来源 | base700 551 / b01 149 / b02 157 / b03 150 / b04 286 | base700 占 42.6%，只来自 36 个种子，单种子最多 18 行 |
| kind | local 723、direct 182、web_local 110、write 70、script 55、refuse 51、smalltalk 42、clarify 35、web 25 | write 70 行里 68 行、script 55 行里 48 行来自 base700 |
| 语言 | 中文 0 行 | 主力用户是中文用户 |
| 轮数 | 单轮 95.1%，2 轮 63 行（全部来自 b04），3 轮及以上 0 | 没有纠错、改需求、换题 |
| 失败 | 工具报错 4 行，全是 `data_query` 参数错 | 没有「找不到 / 查不到 / 写失败」后如实汇报的样本 |
| 终答 | 1015 行带 "Reply with only the final answer"（78%），终答中位 11 字符 | 学不会用自然语言交付结果 |
| 首动作 | `list_files` 62.4%；题面给了路径的 139 行里仍有 77 行先 ls | 仪式化起手 |
| 冗余 | b01–b03 比参考路径多调 1.1–1.6 次；b04（GLM step.py）−0.18 | DeepSeek k=3 路径偏长 |
| 拒绝 | b02/b03 的 28 条是 >400 字符的加粗长文 | 违反「1–2 句」规格 |
| 长度 | p50 1847 / p99 3597 / max 4094 token（ctx 4096） | 多轮会直接顶到上限 |
| UNKNOWN 契约 | 1040 行（80%）题面带 "If you cannot determine the answer, reply exactly UNKNOWN"；56 条终答是裸 `UNKNOWN` | 查不到时只会吐一个固定词：不说找了哪、缺什么、下一步怎么办。真实用户不会给这个契约 |
| 收尾阶段 | 0 行含重复调用被拒 / "Tool execution is complete" 的收尾对话 | harness 收尾路径完全在分布外，见 §1.1 |
| 工具目录 | 1293 行全部是同一套 work-v1 12 个工具 | 模型背熟目录，不读本轮 `<tools>`，见 §1.1 |
| `data_query` | 2019 次 `read_file` 对 62 次 `data_query`（占全部调用 3%） | 表格题只会整读后用 `calculator` 手算 |

### 1.1 v1.2 横测轨迹给出的证据（16 arm × workbank 干净 112 / bfcl-product 60，逐题分类）

| 发现 | 数据 | 对本规划的含义 |
|---|---|---|
| **头号死因：收尾阶段仍吐工具调用** | 重复调用被拒 → harness 进 answer 阶段 → 模型继续输出 `<tool_call>` → `decision_protocol_invalid`。12/14 个 v1.2 state 在干净 112 里死于此 36–66 题、bfcl 18–41 题；100% 由重复调用触发 | 新增 N10 收尾恢复 |
| 锯齿曲线 = 调用倾向二态 | m288 / m432 / m576 工具题零调用率 47 / 24 / 17%、收尾死因 1 / 14 / 12；其余 arm 零调用 2–9%、收尾死因 36–66 | checkpoint 选择要更密、前几名补副本（§6）；N10 让「调个不停」一侧不再致命 |
| 真实工具能力平台约 11/100 | 非 notool 100 题：s158 / s316 / s395 / m432 都是 11；m432 多出的分几乎全来自 notool（9 vs 其余 1–5）；m432 工具题 L2 通过 0/24 | 难题（L2、多步聚合）仍是空白 |
| bfcl 崩在中文 | bfcl-product 的 missing-required 与 multiturn 40 题全是中文、irrelevance 20 题全是英文；基模中文 29/40，所有 state 2–10/40 | N1/N2/N3/N8 方向被证实；bfcl-product 中文 40 题可直接当中文验收 |
| 背熟工具目录 | bfcl irrelevance 只提供 bfcl 自带函数，多数 state 仍去调 `calculator` / `web_search`（s395 一个 arm 60 余次） | §4.2 工具目录轮换 |
| 复读退化是 JSON 标点塌缩 | 输出 `":"":"":…`；mixed 路 11–15 题、suffix 路 1–6 题、基模 2 | 与全文 loss 大量落在工具 JSON 上一致，§2.1 mask 修复后复查（§6 计数） |
| tabular / logs 全场 ≤2 | 37 题；模型不用 `data_query`，`read_file` + `calculator` 手算出错 | 新增 N11 |
| 假拒绝 | m432 零调用题里 10 条是 UNKNOWN / "I can't"，其中 3 条声称 "I have no tools"（m288 更多） | §4.1 规定拒绝必须有依据；N4 必须先有工具尝试 |

## 2. 前置项（开工前必须定下，否则白补）

1. **训练管线**：mask 掉非老师输出、终答后追加 EOD（RWKV-PEFT `--append-eod` 或等价实现）。当前训练器全文算 loss，
   老师输出只占 6.3%；本规划里新增的长工具输出、多轮前文会进一步稀释监督信号。不修，加数据的收益会被吃掉大半。
2. **ctx 长度**：3–5 轮会话在 4096 下放不下。二选一：训练 ctx 提到 8192（推荐，产品会话本来就长）；或 N3 每行硬限
   ≤4000 token、工具输出压到最小。
3. **Web 失败夹具**：`web_fetch` 未命中 URL 时返回的是 `ok:true` + `[fixture] no page matched this URL.`，
   模拟不出真实失败。需给 `WebFixtureEntry` 加 `error`（或 `status`）字段让 fetch 返回 `ok:false`。
   文件侧不用改：读不存在的路径本来就是 `ok:false`。
4. **自然语言终答的判据**：现有 `output_contains`（全含）+ `output_excludes` 够判事实，但没有长度上限。
   在 collect 阶段加字符上限过滤（建议 ≤600 字符），或新增 `max_output_chars` 判据。
5. **中文题试跑**：lint/verify/render 从未跑过中文题面。先出 5 道中文题走完全部闸门，确认无编码或判据问题再批量出。
6. **System 保持英文、不翻译**：wire_hash 必须不变，产品运行时也是这份 System。中文只出现在用户消息、工作区文件和终答里。
7. **顺手修掉的题库问题**：verify.go 里 B 组的破坏测试没有真正生效（`expected_stdout` 未参与比对）；nt-5270 判据补上
   `git stash push -u`。nt-5273 已修为 v2（2026-09-29）。
8. **decontam 看不见中文（阻塞 N1–N11 的中文部分）**：`internal/lab/similarity/similarity.go` 的 `wordRe` 是 `[a-z0-9]+`，
   中文题面分词后为空，5-gram 与专有名维度全部失效（workflow §「本期不出中文题」记过，本规划原稿漏列）。
   需加 CJK 字符 n-gram（建议字 3-gram）并用一道故意近似 bfcl-product 的中文题验证能命中，再放量出中文题。
9. **decontam 的 `--test` 加上 bfcl-product 与 p13-holdout**：N8「缺必需参数」与 bfcl 中文 missing-required
   （如「我需要你处理 TOKEN，但没有提供具体路径。先向我询问路径」）是同一骨架，不查就泄漏进唯一的中文验收。
10. **新管线先重训 v1.2 作基线**：§2.1 换成 mask + EOD 后，b05 若直接对照旧 v1.2，就把「管线」和「数据」两个变量
    混在一起（v1.2 报告对 mixed 数据 + lr 的混杂已吃过亏）。先用新管线、同 lr（1.5e-2）重训 v1.2 mixed，
    作为 b05 / v1.3 的对照组。N10 也依赖 mask（见 §4 N10）。
11. **调用次数判据不用新增**（2026-09-30 更正上一版的说法）：`max_calls` 已有，写在题目级 `expect.max_calls`
    （`{"read_file": 1}`，按工具设上限，见 `internal/agent/eval/expectcheck.go`）；「说查不到之前至少查过一次」写
    `required_tools: ["read_file"]` 即可——`list_files` / `search_text` / `read_file` 三个查找类工具互相认可。
12. **题目级工具子集**（§4.2 用）：workbank / distill 题目现在只能拿整套 work-v1 目录（仅 Primitive 有 `ToolNames`）。
    需给 `Case` 加「本题提供的工具」字段并进 run.json。`wire_hash` 只覆盖目录渲染模式（`catalog=`），不含具体工具，
    所以轮换目录不违反 §2.6。
13. **lint 认识 `tags.answer_style`**（§3.2、§3.3、全部中文题都要用，**阻塞 b05**）：只在 `--canary-prefix DISTILL-CANARY`
    下生效。`unknown`（缺省）= 最后一轮以完整 UNKNOWN 契约结尾（现行规则）；`value` = 以 "Reply with only the final answer."
    结尾且**不得**带 UNKNOWN 半句；`natural` = 两种英文契约都不得出现在结尾（中文题、自然语言作答题）。
    `natural` 题若判据里有 `output_equals: "UNKNOWN"` 报错——那正是要改掉的形态。workbank（默认前缀）行为逐字节不变。

## 3. 存量修复（b05）：扫一遍，不正常的修掉

2026-09-30 对 v1.2 mixed 的 1293 行做了一轮扫描（`bench/distill/tools/v13_scan.py`，结果入库
`bench/distill/v13/scan-v12.json`，逐行列出命中）。只修扫出来的问题，其余存量**原样重新渲染**。

### 3.1 扫描结果

| 模式 | 行 | 来源 | 说明 | 处理 |
|---|---|---|---|---|
| 给了路径还先 `list_files` | 106 | base700 96、b01–b03 10 | 题面写明了要读的文件，起手仍先列目录 | 重解 / base700 剔除 |
| 裸 `UNKNOWN` 终答 | 56 | base700 31、b01–b04 25 | 找了一圈只吐一个词：不说找了哪、缺什么 | 改题后重解（§3.2）/ base700 剔除 |
| Markdown 终答 | 41 | b01–b03（DeepSeek 写的闲聊、拒绝） | 加粗、列表、小标题 | 重解：纯文本 1–4 句 |
| 长拒绝（> 400 字符） | 28 | b02 20、b03 8 | 实际都 > 800 字符 | 重解：1–2 句，做不到什么 + 为什么 + 替代 |
| 长闲聊（> 800 字符） | 12 | b01–b03 | 能力介绍写成长文 | 重解：短版 |
| 套话反问 | 12 | b04 hyb-60xx | "lists two X, A and B. Which one do you mean?" 同一句式 | 重解：换自己的话问 |
| 同一调用发两次 / 同一文件读两次 | 2 / 2 | base700、b02 | 冗余 | 重解 / base700 剔除 |
| 「只给答案」下答了一长句 | 2 | base700 | 违反题面格式 | 剔除 |
| 写文件后只答 `DONE` | 70 | base700 68 | 题面要求 "When finished, reply DONE."，**是契约不是缺陷** | 不动；新增写操作题（N9）改为终答说明改了什么 |

扫描也查过但**不算问题**：简单算式用 `calculator`（86 行，7B 用计算器是好习惯）、8 次以上调用（7 行，都是真的多步）、
工具报错后改对（4 行，好样本）。

合计：b01–b04 **88 道题**要重解（`fix.resolve_cases`），base700 **122 行**剔除（`fix.base700_drop_entries`）。

### 3.2 25 道裸 UNKNOWN 题：先改题，再重解

`fix.absent_cases` 列出的 25 道都是 TR-ABSENT（信息确实不在工作区），判据 `output_equals: "UNKNOWN"`。逐题改：

- 题面删掉整句答案契约，`tags.answer_style = "natural"`，`tags.version += 1`；
- `expect` 改成：`output_contains_any` = 缺失对象的名字（从 NOTES 的 Traps 读，给 2–4 种写法），
  `output_excludes` = `["UNKNOWN"]` + NOTES 里的诱饵值，`required_tools: ["read_file"]`；
- verify.py 与 NOTES 同一次改完（workflow §2.3 的改题规矩），`bank verify --strict-shape` 必须过。
- 重解时终答按 §4.1 第一行写：「查了 A、B，没有 X 的记录；只找到 Y。」

### 3.3 UNKNOWN 契约降到少数（机械改题，不用重解）

`bench/distill/tools/v13_edit_contracts.py`（需先有 §2.13）：凡最后一轮以完整契约结尾的蒸馏题，按题 ID 哈希
1/3 保留完整契约、2/3 删掉 "If you cannot determine the answer, reply exactly UNKNOWN." 只留 "Reply with only the
final answer."。2026-09-30 试运行：保留 204 题、改 406 题、跳过 25 道 absent 题。**旧路径不用重解**：答案没变，
只少了弃权那半句，重新渲染即可。

### 3.4 base700

剔除 122 行后剩 429 行，再按每个种子最多 6 行截断（优先留 script / write / web），约 200 行。base700 来自 v1.1 转换过的
records，**不能重新渲染**：从 v1.2 mixed 的 rendered 行原样取用（去掉末尾 `\n\nUser:` 并同步收回最后一个 loss span，
打包时统一再加），`wire_hash` 必须仍是 `707c6740…`。

### 3.5 存量合计

| 存量 | v1.2 行 | v1.3 行（估） |
|---|---|---|
| base700 | 551 | ~200 |
| b01–b04（88 题重解，其余原样重渲染） | 742 | ~740 |
| b04r（v1.2 之后补的 25 道两轮反问） | 0 | 50 |
| **合计** | 1293 | **~990** |

## 4. 新增

每类都要走 exclude 去污染（`corpus decontam --test bench/workbank/cases`、bfcl-product 以及 §6 的留出集，中文部分依赖 §2.8），**每个种子最多 5 条**，新 family 不复用 base700 种子工作区。
「中文」列表示该类中中文题的最低占比。

| # | 类别 | 行 | 题/会话 | 中文 | 规格 | 判据 | 老师 |
|---|---|---|---|---|---|---|---|
| N1 | 中文单轮工具题 | 200 | ~140 题 | 100% | 把 b01–b04 已验证的 family 改写成中文题，工作区文件内容也换成中文（中文日志、中文表头、中文文档）；≥40% 题面直接给出路径 | 同原 family；数值题用中文约束（「只回答数字」），不带英文 UNKNOWN 模板 | GLM step.py |
| N2 | 中文零调用 | 100 | ~110 题 | 100% | 直答 40、闲聊 25、拒绝 20、反问 15；闲聊不带答案契约 | 同 workflow §4.3 / §4.3.1 | DeepSeek k=3 |
| N3 | 3–5 轮会话 | ~175 | ~50 会话 | 50% | 同一工作区连续 3–5 轮：1/3 中途改需求（「改成按周统计」）、1/3 纠正上一轮（「不对，应该排除测试环境」）、1/3 顺着结果追问或换一个相关问题。纠正轮里约 1/4 是**用户纠正错了**：模型复核后拿证据坚持原答案、说明依据，而不是顺着改 | 每轮独立判；正确的纠正轮要求答案与上一轮不同且正确；错误的纠正轮要求答案不变（`output_contains` 原值 + `output_excludes` 用户给的错值） | GLM step.py |
| N4 | 失败后如实汇报 | 120 | ~100 题 | 50% | 缺文件 / 路径写错 / 数据里确实没有 / `data_query` 列不存在 / 网页打不开（需 §2.3）/ 只能部分回答；终答按 §4.1 写：试过什么、卡在哪、缺什么、下一步。**不带** UNKNOWN 契约 | `output_contains_any`（缺失对象名）+ `output_excludes`（诱饵数值、编造路径、"I have no tools" 类措辞）+ `required_tools: ["read_file"]`（§2.11）；部分回答用 `must_state_unverified` | GLM step.py |
| N5 | 自然语言交付 | 100 | ~90 题 | 50% | 「帮我看看这个项目 / 总结一下这份日志 / 解释这个配置在做什么」；**不带**「只给答案」模板 | `output_contains`（2–4 个必含事实）+ 长度上限（§2.4） | DeepSeek k=3 |
| N6 | 闲聊夹任务 | 80 | ~40 会话 | 50% | 两轮：寒暄后派活、派活后道谢再追问；闲聊轮不调工具 | 闲聊轮 `tools: []`；任务轮按普通题 | GLM |
| N7 | 长文件定位 | 80 | ~60 题 | 30% | 300–2000 行的日志/CSV/源码；要求 `search_text` 定位 + `read_lines` 取窗口，而不是 `read_file` 整读（64 KB 截断远超 ctx） | 值判据；题目级 `expect.max_calls` 限制 read_file 次数 | GLM step.py |
| N8 | 反问多样化 | 60 | ~30 会话 | 50% | 缺必需参数、写操作前确认（覆盖/删除）、多种合理解读；第 2 轮用户补信息后完成 | 第 1 轮问句词表 + `forbidden_tools` 写工具；第 2 轮普通判 | GLM |
| N9 | script / write / web 补覆盖 | 120 | ~80 题 | 30% | script 40、write 40（新建/局部替换/追加）、web 40（含 TR-EARLYHIT 查到就停） | `expect.files` / `expect.run` / 值判据 | GLM step.py |
| N10 | 收尾恢复 | 100 | ~100 题 | 随来源 | 脚本变换，不出新题：`bench/distill/tools/v13_closeout.py` 从已通过的单轮路径里，把一次先前的本地读取原样复制到终答前，标 `supervised:false`；render 时真实 harness 拒绝这次重复、写出收尾提示，原终答照常判分。**插入的重复调用在 loss 区间之外**，所以必须用 mask 训练（§2.1）；全文训练器下不做 N10 | 原题判据 | 无（机械变换） |
| N11 | tabular / `data_query` 聚合 | 80 | ~60 题 | 30% | 50–500 行 CSV/TSV：过滤、分组、求和/均值/计数、多条件；要求 `data_query` 而不是 `read_file` 整读再手算；含 1/4「列名写错 → 看错误信息 → 改对重查」 | 值判据 + `required_tools: [data_query]` + 题目级 `expect.max_calls` 限制 read_file | GLM step.py |
| | **新增合计** | **~1215** | | | | | |

写工具题统一要求：先读后写、改动最小、终答说明改了什么。危险写操作（覆盖已有文件、删除内容）归 N8 先确认。

N10 已于 2026-09-30 在 b01–b04 脚本上实测：取 100 题 → render 96 行，96 行全部含 "duplicate tool call rejected" 与
"Tool execution is complete"，`wire_hash` 不变；另 4 题是原路径在当前题目版本下本就不过的拒绝题。只复制
`list_files` / `read_file` / `read_lines` / `search_text`：`web_search` / `web_fetch` 可重放，重复时会被重新执行而不是拒绝，
走不到收尾；带 `expect.max_calls` 的题也跳过（被拒的重复仍计入预算）。来源用 v1.3 最终通过的脚本，路径编号 `--p81`。

### 4.1 「查不到 / 做不到」时怎么答（全部新增行与重解行适用）

**UNKNOWN 是用户指定的输出格式，不是模型的默认行为。** 只有题面明确要求 "reply exactly UNKNOWN"（或中文等价说法）时才
只答这个词；其余情况按下表，终答 2–3 句、不编造数值：

| 情况 | 终答要写的 | 判据 |
|---|---|---|
| 工作区里确实没有 | 查了哪些文件 / 位置，要找的东西不在其中；有相近信息时指出来（「只找到 X，没有 Y」） | `output_contains_any` 缺失对象名 + `min_calls ≥ 1` |
| 只能回答一部分 | 先给能确定的部分，再点名没能核实的部分 | `output_contains` 已知值 + `must_state_unverified` |
| 工具报错 / 网页打不开 | 什么失败了；换一种方式再试一次，仍不行再如实汇报 | 至少两次不同调用 + 缺失对象名 |
| 超出能力（无删除工具等） | 做不了什么、为什么，给替代办法（让用户执行的命令、可以代做的部分） | `output_contains_any` 限制词 + `output_excludes` 完成声明 |
| 需求有歧义 | 反问（N8） | 问句词表 + `forbidden_tools` |

禁止的形态：没查就说查不到；声称「我没有工具」而本轮 `<tools>` 里其实有可用工具；带契约之外的裸 `UNKNOWN` / 「不知道」。

### 4.2 工具目录轮换（渲染层，作用于全部行）

v1.2 每行都是同一套 12 个 work-v1 工具，模型背熟了目录：bfcl 只提供自带函数时照样去调 `calculator` / `web_search`
（§1.1）。v1.3 起：

- ~40% 的行随机去掉 2–4 个与本题无关的工具（不去掉轨迹里用到的工具），题目级字段见 §2.12；
- N2 / N8 / §4.1「超出能力」中 ~1/3 的题只提供少量工具，其中至少一部分题的答案取决于「目录里没有这个工具」；
- 评测侧统计「调用未提供的工具」次数（scorer 已于 2026-09-30 把它判为失败，见提交 70e604f）。

## 5. 目标构成（v1.3 ≈ 2200 行：存量 ~990 + 新增 ~1215）

| 指标 | v1.2 | v1.3 目标 |
|---|---|---|
| 中文行 | 0% | ≥28%（按 §4 各类下限合计约 32%） |
| 多轮行（≥2 轮） | 4.9% | ~18%，其中 3 轮及以上 ≥8% |
| 失败/部分回答后如实汇报 | 4 行 | ≥160 行（N4 120 + N10 证据不够 40 + 存量裸 UNKNOWN 重解） |
| 带「只给答案」模板 | 78% | ≤50% |
| 带 UNKNOWN 契约 | 80% | ≤20%（§3.3 后存量约 1/3 保留，新增行默认不带） |
| 裸 `UNKNOWN` 终答 | 56 行 | ≤25 行，且全部出现在带契约的题里 |
| 收尾恢复（重复被拒 → 文字终答） | 0 行 | ~100 行 |
| `data_query` 占全部工具调用 | 3% | ≥10% |
| 工具目录不是整套 work-v1 的行 | 0% | ~40% |
| 首动作 `list_files` | 62.4% | ≤35%；题面给路径时 ≤10% |
| base700 占比 | 42.6% | ≤11% |
| 零调用（direct/smalltalk/refuse/clarify 第 1 轮） | 24% | 22–28%（不下降，防 bfcl 过调用） |
| write + script | 9.7% | ≥12%（N9 80 行之外，N3/N8 中至少 1/4 会话含写操作） |
| 单行 token | max 4094 | ≤ 训练 ctx − 64 |

## 6. 留出评测集与验收（留出集与 N1–N11 同时出，不进训练）

workbank 是英文单轮考卷，量不出这次补的方向。另出 **p13-holdout 约 60 题**：中文 20、3 轮以上会话 10、失败汇报 10
（覆盖 §4.1 的前四种情况）、自然语言交付 10、写操作 10。用独立 family，出完先加进 decontam 的 `--test`。

v1.3 的验收四项都报：

| 套件 | 要求 | 说明 |
|---|---|---|
| workbank 干净 112 | 不退 | 对照组是 §2.10 用新管线重训的 v1.2，**不拿 v1.2 m432 的单点 20 当基准**——那是调用倾向二态之间的平衡点，邻点只有 15 / 8 |
| bfcl-product 60 | 中文 40 题要涨，英文 irrelevance 20 题不退 | 中文 40 题是现成的中文 + 多轮 + 追问考卷；v1.2 所有 state 2–10/40，基模 29/40 |
| p13-holdout | 要涨 | |
| 失败形态计数 | 收尾阶段吐工具调用、复读退化、调用未提供的工具、零调用假拒绝都要降 | 按 [classify_failures.py](../evaluations/state-v12-20260929/classify_failures.py) 的口径逐 arm 报 |

checkpoint 选择：每 1/3 epoch 存一个点；前 3 名与对照组各补 2 个副本再定（v1.2 相邻 48 步可差 7–12 题）。

## 7. 分批

| 批 | 内容 | 行（估） | 说明 |
|---|---|---|---|
| b00 基线 | 新管线（mask + EOD）重训 v1.2 mixed | 0 | §2.10；之后每一版都对照它 |
| b05 修存量 | §3：88 题重解（含 25 道先改题）、406 题删 UNKNOWN 半句、base700 剔除 122 行后截断、合入 b04r；§4.2 目录轮换 | ~990 | 不出新题，先把基底修干净；完成后单独训一版，对照 b00，拆开「修存量」的收益 |
| b06 单轮新题 | N1、N2、N4、N7、N9、N10、N11 + p13-holdout | ~800 | 先 5 道中文题试跑（§2.5，且 §2.8 decontam 已支持中文）；N10 先拼 10 条与真实轨迹逐字节比对；每类试 10 题过全闸门再放量 |
| b07 会话 | N3、N5、N6、N8 | ~415 | 依赖 §2.2 的 ctx 决定；先抽 10 个会话看 token 分布 |

每批验收除 workflow S7 外，加查：§5 各指标、单种子行数上限、中文题人工抽 20 条看是否自然（不是英文题直译腔）。

## 8. 待拍板

1. ctx 是提到 8192，还是保持 4096 并压缩会话（§2.2）。建议 8192：v1.2 p99 已 3597，多轮加上 N10 的拼接只会更长。
2. ~~中文题是否一律去掉 UNKNOWN 契约~~ → 已扩大为中英文都降到 ≤20%，并按 §4.1 规定「查不到 / 做不到」的答法（2026-09-30）。
3. b05 修完是否单独训一版（推荐，用来拆分收益），还是 b05–b07 合并一次训。建议单独训，但对照组是 b00，不是旧 v1.2。
