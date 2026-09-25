# 冒烟批次报告（M1，batch `smoke`）

> 按 [distill-workflow.md](../distill-workflow.md) §3 S1–S7 跑完一轮的最小批量，用来在开 b01 之前把整条管线（含 M0 的工具改造）真实走一遍。

> 日期：2026-09-25。执行：主控 Agent。
> **2026-09-25 作废说明**：本报告的老师数据是在 harness **v21** 上跑的。同一天发现并修复了 md-fence 解析器
> 把终答从第一个围栏处截断的缺陷（harness **v22**，commit `1d92d15`），因此本批的 14 道题连同数据
> 已在 `b01` 里按 v22 **重跑**（同一轮老师跑覆盖 225 题），行数、pass@k、抽检结论以
> [b01.md](b01.md) 为准。本文件保留的是当时的过程记录与三条发现（§6），其中 §6.3 的围栏截断
> 已在 v22 修复，不再是待决项。

## 1. 结论

- **管线可用**：14 题 × k=3 全过、`paths` 出 18 条路径、`render` 18 行 0 拒绝、`pack --dry-run` 退出 0、`wire_hash` 与 S0 记下的 g1k 值一致。
- **入库 14 题，下架 0 题**；`0/3` 题 0 道（pass@3 全部 3/3）。
- 抽检 18 行（全量，本批只有 18 行）**全部合格**，剔除 0 行。
- 过程中发现 3 件事，已处理或已记录，见 §6。

## 2. 起点与参数

| 项 | 值 |
|---|---|
| 题数 | 14（10 个场景各 1 题 + notool 5 道闲聊） |
| 起草 | 8 个子 Agent 各 1 题（每场景）+ 文档 §2.5 的 `tab-5001` 样例 + 已有 `nt-5001..5005` |
| 老师 | `deepseek-flash`（next-token.cc 中转，`/v1/chat/completions`），`temperature 0.3`、`top-p 1`、k=3 |
| 老师并发 | `--case-parallelism 4`（该端点 40 并发会被 `503 system_cpu_overloaded` 打满，见 09-21 基线报告） |
| 老师预算 | `--max-steps 16 --max-tokens 4096 --decision-max-tokens 8192`、`--tool-catalog work-v1 --file-tools lines` |
| 学生 wire | `wire_hash 707c67403b1b2e5269ddfcd8ecee2bfb7ce4d8133912d102bc67f1324f8018cb`（harness `rwkv-agent-eval-v21`，scorer v3） |
| `bin/rwkv-cli` sha256 | `2bcdedbc65cf9426e02aeb15569918af9f36395e5db8207b30806a52f47e2185` |
| 代码 commit | `b2072effb1d179704cc845ff8815665d3de2b279`（M0 工具改造） |

## 3. 静态闸门（S2/S3）

| 闸门 | 结果 |
|---|---|
| `bank lint --canary-prefix DISTILL-CANARY --cases bench/distill/cases` | 14 题，**0 违规**，退出 0 |
| `bank verify --cases bench/distill/cases` | 14/14 PASS，退出 0（闲聊 5 题按 §4.3 记 `verify_skipped_smalltalk`；`web-5001` 无本地文件记 `sabotage_skipped_no_files`） |
| `bank dedup --cases bench/distill/cases` | **无命中** |
| `bank hitcheck`（web/hybrid） | 2/2 通过，各 5/5 改写查询命中 |
| `corpus decontam` vs `bench/workbank/cases` | 14 候选，**0 flagged**（prompt/files/names 三维全 0） |
| `corpus decontam` vs `bench/workbank/cases-shelved` | **0 flagged** |

## 4. 老师跑（S4）与选路（S5）

三轮 `teacher2-k0/k1/k2`（fixture 修好后的最终一轮）：各 14/14 通过，**infra 错误 0**，invalid 0，protocol 100%。

pass@3 分布：**3/3 = 14 题**（无 2/3、1/3、0/3）。

`paths` 结果：14 题保留 **18 条路径**，14 题全部至少 1 条。

| 丢弃原因 | 条数 |
|---|---|
| same tool sequence | 16 |
| tool error or rejection | 4 |
| answer repaired by the harness | 2 |
| duplicate path | 1 |
| over per-case cap | 1 |

## 5. 重放切行（S6）与打包（S7）

- `render`：`18 rows written from 18 cases, 0 cases rejected`；`run.json` 的 `wire_hash` = `707c6740…`（= S0 值）。
- `pack --dry-run` 退出 0：18 行、单一 wire_hash、最长 4041 token（≤ 4096）、无 canary、无重复行。
- 场景分布：notool 5、config 2、hybrid 2、tabular 2、web 2、code/docs/filesystem/logs/script 各 1。
- **零调用行 5/18 = 27.8%**（下限 15% 只打印不拦截；这 5 行全是闲聊）。
- kind 分布：local 8、smalltalk 5、web_local 4、script 1。
- token：p50 1966 / p99 4041 / max 4041。

### 抽检（主控亲读 `text` 里老师输出的部分）

本批只有 18 行，**全量抽检**而不是随机 20 行：

| 题 | 老师终答 | 判定 |
|---|---|---|
| code-5001 | `4` | 对 |
| doc-5001 | `21` | 对 |
| fs-5001 | `screening-sat.txt` | 对 |
| log-5001 | `5` | 对 |
| tab-5001 ×2 | `5` | 对 |
| cfg-5001 ×2 | `576` / `576 MB` | 对（单位可接受） |
| hyb-5001 ×2 | `£4,105.35` / `£4105.35` | 对 |
| web-5001 ×2 | `6` | 对 |
| scr-5001 | `DONE` + 修复说明 | 对（改对了 `void`/`voided`） |
| nt-5001 | `Good morning! How can I help you today?` | 对（真在寒暄，无工具调用） |
| nt-5002/5003/5004 | 身份 / 能力 / 工具清单 | 对（答的是问题本身） |
| nt-5005 | `Sounds good — glad I could help…` | 对 |

**剔除 0 行**。没有出现「答非所问却撞上 `output_contains_any` 关键词」的情形（5 道闲聊题的关键词命中都发生在真正的寒暄/能力描述里）。

## 6. 本批发现（三条，都已处置或需用户拍板）

### 6.1 闲聊题的 `bank verify` 需要与 lint 一致的豁免（已改）

§4.3 只写了 lint 的豁免，但 S2 要求 `bank verify` 退出 0，而闲聊题没有 `verify.py`（没有可独立计算的答案），会报 `verify_py missing` 硬失败。
**处置**：`bank verify` 对 `task_type == smalltalk` 且无 `verify.py` 的题记 `verify_skipped_smalltalk`（ok），其它 task_type 仍硬失败。已加回归测试。

### 6.2 一道题的 fixture 超预算，按 allocation-v1 §5 缩 fixture 后重跑（已处理）

首轮 `log-5001--p1` 4262 token 超 4096。该题**所有**路径都超长，按 [distill-allocation-v1.md](../distill-allocation-v1.md) §5「缩 fixture 后重跑老师」处置：
fixture 从 5256 字节缩到 3644（README 精简、轮转日志 `.log.1` 压缩），保留 5 条终态行、12 条 refusal 诱饵、`.log.1` 的 5 条——陷阱与答案不变，`lint`/`verify`/`dedup` 重跑全绿，`tags.version` 1 → 2，然后重跑整轮 k=3。
最终 `log-5001--p1` 3020 token。

**给 b01 的经验**：4096 是硬上限，固定开销约 950 token，多步轨迹的回执与 post-tool 提醒都要算进去。短收尾题 fixture ≤ 3KB，其余 ≤ 4KB，`ref_calls` ≤ 4，别贴着上限出题。

### 6.3 脚本类题的路径会被「answer repaired」吃掉（需用户拍板，对应 §8「回答风格」）

`scr-5001` 首轮 3/3 通过但 **3 条路径全丢**，原因是老师在 `DONE` 之后附了一段说明并用 ` ``` ` 围栏贴出最终输出；在 md-fence wire 下围栏会被解析成工具调用，harness 因此修整了终答，`paths` 按规则丢弃（§3 S5）。
第二轮只剩 2 条 repaired（另一条活了下来），最终 `scr-5001` 出 1 行。

这不是题目缺陷，是**老师风格 × harness 围栏语法**的相互作用，也正是 §8「回答风格」列出的待决项。三个选项的实测依据：

1. **接受**：脚本类题会稳定损失一部分路径（本批 3→1）。写文件类题的终答本来就不进 loss（`kind == script` 的行训练的是动作与修复过程），损失的是轨迹多样性不是正确性。
2. **抽检剔除**：不解决问题——被丢弃的路径根本到不了抽检。
3. **给老师加只对老师生效的风格提示**（老师的 wire 不进数据）：能直接提高脚本类题的产出率，但要改 `agent-eval` 代码。

## 7. 入库清单

| 路径 | 内容 |
|---|---|
| `bench/distill/cases/{code,config,docs,filesystem,hybrid,logs,script,tabular,web}/*-5001/` `notool/nt-5001..5005` | 14 题（`case.json` / `verify.py` / `NOTES.md`） |
| `bench/distill/batches.jsonl` | 本批记录 |
| `bench/distill/reports/smoke.md` | 本报告 |
| `bench/distill/exclude.jsonl` | 本批**无新增**（无剔除行） |

`runs/distill/smoke/**` 不入库（`runs/` 已 gitignore）。
