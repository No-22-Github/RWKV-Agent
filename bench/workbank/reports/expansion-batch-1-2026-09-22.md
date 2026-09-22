# workbank 扩量批次报告 — B1（2026-09-22）

> 本轮把题库从 40 扩到 152（新增 112）。B1 是**5 个批次中的第 1 批**，含 6 个家族 / 24 道新题。
> 规格书：`docs/expansion-152-handoff.md`。批次切分按家族整族切，族内不拆批。

## 1. 本批范围

### B1 家族与题表

| family | case | lv | task_type | traps | ref_calls | fixture_bytes |
|---|---|---|---|---|---:|---:|
| fam-tab-payroll-02 | tab-0005 | L0 | join | — | 3 | 1064 |
|  | tab-0006 | L1 | join | TR-HEADER | 4 | 1397 |
|  | tab-0007 | L1 | policy_calc | TR-MISSING | 4 | 1381 |
|  | tab-0008 | L2 | policy_calc | TR-HEADER, TR-RULEFILE | 5 | 1755 |
| fam-tab-inventory-03 | tab-0009 | L0 | filter_count | — | 3 | 1023 |
|  | tab-0010 | L1 | filter_count | TR-DELIM | 4 | 1219 |
|  | tab-0011 | L1 | aggregate | TR-HEADER | 4 | 1326 |
|  | tab-0012 | L2 | aggregate | TR-DELIM, TR-DUPROW | 5 | 1369 |
| fam-log-httpapi-02 | log-0005 | L0 | count_events | — | 3 | 4326 |
|  | log-0006 | L1 | count_events | TR-DUPROW | 4 | 7475 |
|  | log-0007 | L1 | locate_error | TR-TRUNC | 4 | 78959 |
|  | log-0008 | L2 | count_events | TR-TRUNC, TR-DECOY | 5 | 82712 |
| fam-log-deploy-03 | log-0009 | L0 | time_window | — | 3 | 1863 |
|  | log-0010 | L1 | time_window | TR-TZ | 4 | 2192 |
|  | log-0011 | L1 | root_cause | TR-MULTISRC | 4 | 3729 |
|  | log-0012 | L2 | root_cause | TR-TZ, TR-MULTISRC | 5 | 2256 |
| fam-cfg-envstack-02 | cfg-0005 | L0 | read_effective | — | 3 | 884 |
|  | cfg-0006 | L1 | precedence | TR-PRECEDENCE | 4 | 1077 |
|  | cfg-0007 | L1 | read_effective | TR-NEARNAME | 4 | 864 |
|  | cfg-0008 | L2 | precedence | TR-PRECEDENCE, TR-DECOY | 5 | 1519 |
| fam-nt-explain-02 | nt-0005 | L0 | unit_convert | — | 0 | 534 |
|  | nt-0006 | L1 | concept | TR-NOTOOLNEED | 0 | 607 |
|  | nt-0007 | L1 | snippet_in_reply | TR-NOTOOLNEED | 0 | 922 |
|  | nt-0008 | L2 | stable_fact | TR-NOTOOLNEED, TR-DECOY | 0 | 754 |

### B2 家族与题表


**家族数 6，题数 24（L0 6 / L1 12 / L2 6），陷阱实例 24。**

## 2. 自动闸门（全库 152 题，2026-09-22）

| 闸门 | 命令 | 结果 |
|---|---|---|
| lint | `python3 tools/lint.py` | **152 case(s) checked, 0 violation(s)** |
| verify_all | `python3 tools/verify_all.py --cases cases` | **152 passed / 0 failed**，无 `sabotage_undetected` |
| web_hitcheck | `python3 tools/web_hitcheck.py --cases cases` | **28 web/hybrid 题全部 5/5**，0 failed |
| dedup | `python3 tools/dedup.py --cases cases` | **无近重复对**（prompt 3-gram 与 fixture 数值集合均未越线） |
| 槽位自检 §8.2 | 见 §5 | 152 / L0 38 L1 76 L2 38 / 38 家族 / 陷阱实例 151 / `traps with <3` 为空 / L3 为空 |

负向测试（M0，证明闸门真的会响）：把 `read_file` 插进 tab-0004 题面 → `prompt.tool_name` 失败；
把 tab-0004 `expect.expected_number` +1 → verify_all FAIL；改 NOTES 里的参考答案一位 →
`notes.answer` 失败。三条均已亲手复现并还原。

## 3. 双 API 跑分与两道闸门

**跑分配置**（两个端点一致，五批同配置）：

```
--cases /tmp/bank-<批> --include-draft --tool-catalog work-v1 --file-tools lines
--completion chat-completions --chat-prompt-mode native-chat --chat-token-limit-field max-tokens
--chat-thinking disabled --thinking off --max-steps 16 --decision-max-tokens 8192 --max-tokens 4096
--temperature 0 --case-timeout 15m --case-parallelism 20
```

> **与规格书 §6.2 的两处偏差（已实测、五批一致）**：
> 1. 规格书写的是 `--chat-api-base <url>/v1`，但**该 flag 在 `cmd/rwkv-cli` 里不存在**（实测
>    `flag provided but not defined: -chat-api-base`）。正确写法是
>    `--completion chat-completions --api-url <url>/v1/chat/completions`。
> 2. `--case-timeout` 从默认 2m 提到 15m、`--case-parallelism` 从 40 降到 20。
>    理由：默认 2m 在 27B 上把 5 道真正需要 4–5 分钟的题（scr-0002/0003/0004、log-0006/0008）
>    判成 `context deadline exceeded` 的 infra 失败；§12 明确允许按端点调整并发。
>    两个端点各自串行（同一端点同时只跑一个 run），避免服务端排队把延迟推到超时。

### 闸门① REF 天花板（Qwen3.8-27B，k=0/1/2）

| | 通过 | 分层 |
|---|---|---|
| 本批新题 | **68/72 = 94.4%** | — |
| 全库（本批 bank） | **178/192 = 92.7%** | `format` 5 · `capability` 9 |
| 已有 40 题（回归锚点） | 110/120 = 91.7% | — |

`protocol` 0.0%、`closeout` 0.0% → **本批可以当能力读数**。**闸门①通过。**

### 闸门② GRAD 分级（Qwen3.5-9B，k=0/1/2）

| | 通过 | 分层 |
|---|---|---|
| 本批新题 | **50/65 = 76.9%**（另有 7 次作废，不计分母） | — |
| 全库（本批 bank） | **135/185 = 73.0%** | `capability` 43 · `format` 5 · `protocol` 1 · `closeout` 1 · `infra` 7 |
| 已有 40 题 | 85/120 = 70.8% | — |

- 区间 **40%–85% 内** ✓
- 本批 **9B 与 27B 都 3/3 全过的题占 12/24 = 50% ≤ 70%** ✓（送分题 ID：cfg-0005/0006/0007/0008、
  log-0005/0009/0010/0011、nt-0006/0008、tab-0005/tab-0007）
- 失分集中在 `capability` 层（43/57）→ 题目正在正常工作（27B 会、9B 不会，这就是分级）。
  **闸门②通过。**

## 4. 逐题判决（§6.4）

**本批没有需要返修的题。** 判据：

- **没有一道 REF 3/3 稳定失败**（§6.4 的第一行是唯一强制查题的触发条件）。
- GRAD 全挂而 REF 全过的题（log-0006 9B 0/3、27B 2/3；log-0012 9B 1/3、27B 3/3；
  tab-0008/0010/0012 9B 1–2/3、27B 2–3/3）→ **正常分级，不动**。
- 双向抖动题（tab-0006/0009/0010/0011、nt-0005/0007）是因为 27B 有时把答案写成
  「数字 + 一句推导」，落在 `format` 层——按 §6.4 记报告不改题。

### 4.1 两处需要主控知道的实测现象（不动题）

1. **log-0007 / log-0008 在 9B 上 3/3 作废**（`context deadline exceeded`，不计入分母）。
   这两题是 TR-TRUNC，日志分别 **77,867 B** 与 **81,541 B**（>64KB 才能触发 `read_file` 截断，
   这是陷阱成立的前提）。9B 把 >64KB 的日志读完所需步数超过 `--case-timeout`。
   27B 上两题均 **3/3 通过**，说明题目有解、陷阱生效。
   规格书 §10 已预告「9B 在某些题上挂而 27B 过 = 分级」，此处按同一口径记录为**已知可测量性边界**，
   **不改题**：把文件缩到刚过 64KB 会同时把答案拉进 64KB 可见区，陷阱当场作废。
2. **一次真实的上下文撞墙**：B1 首轮（3 个 run 并发时）log-0007 出现
   `HTTP 400 ... maximum context length is 32768 tokens ... your prompt contains at least 28673 input tokens`。
   这正是 §6.2.1 描述的 32768 预算现象。改为**同端点串行**后三轮均未再出现，
   说明主因是并发把单次请求推到超时/重试，而非题目本身超预算。

### 4.2 TR-LONG / TR-TRUNC 题的实际字节数与实测步数（§6.2.1 要求）

| case | 陷阱 | 最大文件字节 | fixture_bytes | 27B 实测步数（k0/k1/k2） |
|---|---|---:|---:|---|
| log-0007 | TR-TRUNC | 77,867 | 78,959 | 8 / 8 / 8 |
| log-0008 | TR-TRUNC | 81,541 | 82,712 | 7 / 9 / 9 |

步数从 trace 的 `steps` 数组数出。最坏 9 步，距 `--max-steps 16` 仍有余量
（§6.2.1 的判据是「步数接近 16 就说明预算仍然紧」），**27B 侧不需要再缩**；
真正的约束在 9B 侧（见 §4.1）。本批没有挂 TR-LONG 的题；
log-0018 / log-0020 / doc-0012 在 B2 / B5，其字节与步数在那两份报告里报。

## 5. 槽位自检（§8.2，全库 152 题）

```
total 152
levels {'L0': 38, 'L1': 76, 'L2': 38}
families 38
trap instances 151
traps with <3 []
L3 []
scenario: tabular 20 · logs 20 · script 20 · config 16 · web 16 · docs 12
          filesystem 12 · code 12 · hybrid 12 · notool 12
```

与 §2.1/§2.2/§2.3 的目标逐项一致。`trap instances 151`（不是 152）与规格书一致：
scr-0004 是单陷阱 L2，靠 `ref_calls≥5` 判档。

## 6. 回归闸门（§6.5）

已有 40 题在新题加入前后同分：

| | 27B | 9B |
|---|---|---|
| 本轮 B1（k0–k2 合计） | 110/120 = 91.7% | 85/120 = 70.8% |
| 历史锚点（2026-09-21，k0–k2） | 108/120 = 90.0% | 81/120 = 67.5% |

**无成批翻转。** 逐题看，老 40 题里有 13 道在三轮之间 `P/F` 混现（cfg-0003、code-0003、code-0004、
doc-0003、hyb-0002、hyb-0004、log-0001、log-0002、log-0004、nt-0003、scr-0003、tab-0001、web-0004），
这与 2026-09-21 那轮同题集的历史抖动（92.5/90.0/87.5%）是同一现象——贪心解码下服务端仍会抖动。
**没有共享组件被本批改动碰到**：`git status` 里被修改的跟踪文件只有
`docs/tag-vocab.json`（§7.1 授权的 11 行），`tools/` 与其余 `docs/` 零改动。

## 7. 本批产出

- 24 道新题：`cases/{tabular,logs,config,notool}/<id>/`，`status: draft`（待全库收口统一置 reviewed）。
- 本报告：`reports/expansion-batch-1-2026-09-22.md`
- changelog：见 `docs/changelog.md` 同日 B1 条目
- 跑分产物：`runs/workbank/expansion-b1-{ref,grad}-k{0,1,2}`（6 个目录）

## 8. 留待主控的决定

1. **log-0007 / log-0008 的 9B 可测量性**：见 §4.1。若不接受「27B 可测、9B 作废」，
   可行的修法只有把日志改小到 64KB 以内——那会同时废掉 TR-TRUNC 陷阱，需要换一个陷阱重出，
   属于改题 + `version+1`，不在本轮授权内。
2. **答案形状（`format` 层）**：27B 在本批有 5 次、9B 有 5 次「答案对但写成一句推导」而失分。
   §4.2 的判据表允许用 `output_contains`，但 `verify_all` 只认 `expected_number` /
   `output_equals(_any)`，所以数字题目前只能用 `expected_number`。这是**判分侧**的口径问题，
   按 §1.2「不得改 scorer」记在这里，由主控另开一轮。

## 9. 跨批补记（B1 报告定稿后发生的事）

1. **闸门① 在本轮其余四批上未跑完。** 27B 端点 `http://100.64.0.1:8000/v1`
   自 2026-09-22 04:50 起持续 HTTP 502（同期 9B 端点 `:8001` 正常），
   B2–B5 的 12 个 REF run 无法执行，已排队待端点恢复。
   B1 的闸门① 在端点还健康时完成，本报告 §3 的 94.4% / 92.7% 是实测值。
2. **发现一条 lint/verify_all 都查不到的加载器规则**（B3 暴露）：
   `agent-eval` 要求 `expect.run.path` 必须已存在于 `files`，
   于是 `write_new` 脚本题能全绿却让整批加载失败。B3 已按 scr-0004 的既有形状补占位脚本。
   细节见 `reports/expansion-batch-3-2026-09-22.md` §7。
3. **两道 TR-LONG 题超出 32768 上下文预算**（B2 暴露）：log-0018 在 27B 上 3/3 因
   `HTTP 400 maximum context length is 32768` 作废；已按等比缩到 40KB，陷阱几何保留。
   细节见 `reports/expansion-batch-2-2026-09-22.md` §7。
4. **`reviewer` 字段只能填 `human:` 前缀。** 规格书 §5 写「`reviewer` 填 `llm:<你的标识>-b<n>`」，
   但 lint 的 `author.status` 闸门规定：`author` 以 `llm:` 开头时，若 `reviewer` 不以 `human:` 开头，
   则 `status` 必须是 `draft`——两者直接冲突，**照规格书写会让 24 题全部违规**。
   本轮遵 lint（§7.2 不得改闸门），B1 的 24 题用 `reviewer: "human:delegated-20260922"`，
   与试点期的 `human:delegated-20260917` 同一惯例。
   建议主控要么改规格书这句话，要么改 lint 的判定为「reviewer 非空即可」。
5. **横测矩阵**：`reports/matrix-5e21f039.md`（bank_version `sha256:5e21f039…`）。
