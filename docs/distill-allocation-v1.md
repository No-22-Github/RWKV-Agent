# 蒸馏加题分配 v1（在 700 条基础上）

> 读者：执行 [distill-workflow.md](distill-workflow.md) 的主控 Agent。流程、命令、闸门都以那份文档为准；
> 本文只规定**加多少、加什么、每行多长**，并**取代**其中 §2.4 的 b01 配额表。
> 写于 2026-09-25，所有数字都是在 main 的当前 harness（`wire_hash 707c6740…`）下实测的。

## 1. 起点：700 条的实际状况

`datasets/workspace-agent-700-20260920/generated/normalized/all.jsonl` 用当前 harness 重渲染（`corpus render --records`，3.5 秒）：
**670 行可用**；30 条被拒，原因是 09-21 scorer v3 之后数据没有重验，明细见 [harness-corpus-render.md](harness-corpus-render.md) 末节。

| 项 | 现状 | 问题 |
|---|---|---|
| 场景 | config/code/docs/filesystem/hybrid/logs/script/tabular 各 80、web 60 | **没有 notool** |
| 零调用直答 | **0 行** | 首动作 100% 调工具，09-23 state 训练 bfcl 崩溃就是这个分布导致的 |
| 多轮 | 0 行 | 没有反问、澄清 |
| 调用次数 | 3–6 次占 84%；1–2 次仅 64 行 | 短轨迹少，学不会收尾 |
| 终答 | 值 487 / DONE 162 / UNKNOWN 51 | |
| `data_query` | 49 行用过 | |
| 恢复前缀 | 119 行（670 中） | 见 §2 决定 2 |
| 种子 | 36 个，全是 workbank 各场景的 0001–0004 | 见 §2 决定 1 |
| token（World 词表） | p50 2095 / p90 2766 / p99 3304 / max 3703 | 在 4096 内 |

## 2. 两个已定的决定（2026-09-25 用户确认）

1. **700 条保留，但 workbank 分数必须分两栏报。** 种子题 36 道（`cfg/code/doc/fs/hyb/log/scr/tab/web` 的 `-0001`～`-0004`）已经被整族泄漏，
   它们的分数不代表能力；其余 112 题是干净分数。`nt-0001..0004` 没有被当成种子，算干净题。
2. **剔除 119 行恢复前缀。** 当前 state 训练器对全文计算 loss，恢复前缀里老师的错误动作会被当成正确示范学进去。
   清单已生成：`bench/distill/exclude.jsonl`（`batch: "base700"`），打包时用 `corpus pack --exclude` 过滤。
   等训练器支持 `loss_spans` 后删掉这 119 行即可恢复，数据本身不删。

基础可用行：670 − 119 = **551**。

## 3. 加多少

**约 650 题 → 约 800 行，总量约 1350 行。** 零调用行约 360 条，占总量约 27%。

换算依据：零调用题每题最多 1 条路径（工具序列都是空的，`paths` 按工具序列去重），按 0.9 行/题估；
调工具的题每题最多 2 条路径，按老师通过率 85% 估 1.5 行/题；多轮题每轮 1 行。

## 4. 怎么分配

| # | 类别 | 目标行 | 题数 | 场景 / task_type | 规格 |
|---|---|---|---|---|---|
| A | 直答 | 180 | 200 | notool：concept 60、unit_convert 45、stable_fact 45、snippet_in_reply 50 | `tools: []`；workspace 里放无关文件作干扰（TR-NOTOOLNEED） |
| B | 闲聊 | 60 | 60 | notool：smalltalk | 问候、道谢、你是谁、能做什么、有哪些工具；**无答案契约**（workflow §4.3）；不筛老师身份 |
| C | 超能力拒绝 | 40 | 45 | notool beyond_capability 29 + config/filesystem 各 8 | 要求发邮件、删文件、执行命令、访问内网等；`forbidden_tools` 含写工具；**不带 UNKNOWN 答案契约**，判据带 `output_excludes: ["UNKNOWN"]`（§4.3.1），允许先查工作区再拒绝 |
| D | 歧义反问（两轮） | 80 | 45 | notool ambiguous_request 20 + hybrid multi_turn 25 | 第 1 轮的反问是判据（`output_contains_any` 问句词表），第 2 轮给出澄清后按普通题判。**配额按 `kind == clarify` 统计，不要求第 1 轮零调用**：老师先翻工作区再问也计入。要拿零调用反问，只有「工作区里没有可查的东西」才自然成立——notool 的 ambiguous_request 按这个出：缺的必须是只有用户知道的信息（哪个客户、哪个月、哪个单位），工作区与问题无关 |
| E | 短收尾 | 160 | 110 | 9 个工具场景各 12（tabular 14） | L0，`ref_calls` 1–2，0 个陷阱；答案在第一个打开的文件里就能找到 |
| F | UNKNOWN + 姊妹题 | 60 | 40 | tabular/logs/config/docs 各 5 对 | 每对：一道数据里确实没有答案（期望 `UNKNOWN`），一道同骨架但有答案 |
| G | 大表 `data_query` | 60 | 40 | tabular 30 + logs aggregate_jsonl 10 | 表 40–120 行，列干净（不带 `$`、`%`、`NA`，`data_query` 解析不了这些）；fixture 仍受 §5 限制 |
| H | 查到就停 | 40 | 30 | web 20 + hybrid 10 | TR-EARLYHIT，`expect.max_calls: {"web_search": 1}` |
| I | 补覆盖 | 120 | 80 | code find_callers/root_cause 各 10、logs time_window/root_cause 各 10、docs link_check/latest_version 各 10、filesystem duplicates/largest 各 10 | 700 条里最少的题型 |
| | **合计** | **800** | **650** | | 零调用行 = A 180 + B 60 + C 40 + D 第 1 轮 45 ≈ 325–360 |

**分 3 批，每批按比例各取三分之一**（b01 约 220 题、b02/b03 各约 215 题），这样每批自身就是均衡的。
每批跑完先看 `paths` 的 pass@k 和 `pack --dry-run` 的统计，再开下一批；某一类行数明显不够就在下一批补。

难度：E 全部是 L0；A/B/C 是 L0–L1；其余按 authoring-guide §4 计算，L2 不超过本批的 20%，不出 L3。

## 5. 上下文预算：每行 ≤ 4096 token

每行 = 系统块与工具目录（固定约 **950** token，实测闲聊行 975–1323）+ 题面 + 每次工具回执 + post-tool 提醒 + 老师输出。
fixture 读进来就会全文进入上下文，所以预算实际上由出题决定：

| 约束 | 值 | 理由 |
|---|---|---|
| 陷阱 | **禁用 TR-LONG、TR-TRUNC** | 这两个陷阱的定义就是 40KB 以上或者会被截断，放不进 4096 |
| `files` 合计 | **E 类（短收尾）≤ 3KB；G 类（大表）≤ 6KB；其余 ≤ 4KB** | 英文约 4 字节/token；v22 修掉围栏截断后老师的终答完整保留、行普遍变长（b01 有 4 行超限被剔），预算按此收紧 |
| 参考解需要读的内容合计 | ≤ 4KB | 老师往往读得比参考解多，要留余量 |
| web 页面 `content` | 每页 ≤ 2KB，每题 ≤ 2 页 | `web_fetch` 回执是全文 |
| `ref_calls` | ≤ 6；script 题 ≤ 8 且 files ≤ 4KB | 每步还有约 60–100 token 的提醒 |
| 多轮题 | **两轮合计 ≤ 4KB**，且满足上面几条 | 第 2 轮那一行包含第 1 轮的完整历史 |
| 老师终答 | 不限，但 answer 阶段硬上限 4096 输出 token | Qwen 的直答常带 Markdown 列表，偏长 |

**批次指标**：超长剔除行 ≤ **2%** 算正常；超过 2% 就在下一批继续收紧本节的数值，**不放宽 4096**（b01：4/366 = 1.1%）。

超过 4096 的行：写进 `bench/distill/exclude.jsonl`（`reason: "over-4096"`），**不截断、不改老师输出**。
同一题的路径全部超长，说明题出得太重：缩 fixture 后重跑老师。`pack` 的 `--max-tokens 4096` 闸门兜底。

## 6. 来源规则补充

起草子 Agent 除了 workflow §2.1 的禁读清单外，**也不得读 `datasets/workspace-agent-700-20260920/`**：那里的题都是 workbank 种子题的变体，读了等于间接用测试题当种子。
700 条只用于重渲染和打包，不作为出题参考。

## 7. 最终打包

```bash
bin/rwkv-lab corpus pack \
  --rows runs/distill/base700/rows.jsonl \
  --rows runs/distill/b01/corpus/rows.jsonl --rows runs/distill/b02/corpus/rows.jsonl --rows runs/distill/b03/corpus/rows.jsonl \
  --exclude bench/distill/exclude.jsonl --max-tokens 4096 \
  --out runs/distill/dataset-YYYYMMDD
```

四份 rows 必须由**同一个** `bin/rwkv-cli` 渲染（`wire_hash` 相同）。换过二进制就把 base700 和各批的 `script.jsonl` 全部重新 render 一遍，只要几秒钟。
