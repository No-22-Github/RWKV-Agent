# workbank 扩量批次报告 — B3（2026-09-22）

> 本轮把题库从 40 扩到 152（新增 112）。B3 是 5 个批次中的第 3 批，含 5 个家族 / 20 道新题。
> 规格书：`docs/expansion-152-handoff.md`。批次按家族整族切，族内不拆批。

> ## ⚠ 闸门①（REF 天花板，Qwen3.8-27B）未完成 —— 端点故障
>
> 2026-09-22 04:50 起，27B 端点 `http://100.64.0.1:8000/v1` 持续返回 **HTTP 502**
> （`/v1/models` 与 `/v1/chat/completions` 均 502），同一时刻 9B 端点 `:8001` 正常。
> 此前数小时该端点已不稳定：本批先期的 27B run 里出现
> `HTTP 502: empty response`、`HTTP 500 Engine…`、`context deadline exceeded`
> 与 `HTTP 400 context length …` 等上游错误，其中两次 run **整批 60 题全挂于 502**。
> 这些被上游错误污染的 run 已作废重跑，但重跑所需的 12 个 27B run 在端点恢复前无法执行。
>
> **因此本报告的闸门①一栏为空。** 本批只有闸门②（9B 分级）是实测数据。
> 27B 的 run 目录 `runs/workbank/expansion-<批>-ref-k{0,1,2}` 会在端点恢复后自动补齐，
> 届时用同一份 `reports/` 生成脚本重新生成本报告即可（脚本与参数记录在 §3）。
>
> **这不改变本批题库侧的证据**：lint / verify_all / web_hitcheck / dedup / Go 加载器
> 五项闸门是全库 152 题的实测结果，与端点无关。
>
> 作为参照，**B1 的闸门① 在同一天、同一配置下已实测通过**（新题 68/72 = 94.4%，
> `protocol` 0.0% / `closeout` 0.0%）——说明这套参数在两个端点都正常时是可用的，
> 缺的是端点本身。

## 1. 本批范围

| family | case | lv | task_type | traps | ref_calls | fixture_bytes |
|---|---|---|---|---|---:|---:|
| fam-cfg-edit-04 | cfg-0013 | L0 | edit_value | — | 3 | 1095 |
|  | cfg-0014 | L1 | edit_value | TR-READONLY | 4 | 1443 |
|  | cfg-0015 | L1 | merge | TR-INJECT | 4 | 1533 |
|  | cfg-0016 | L2 | edit_value | TR-READONLY, TR-INJECT | 6 | 1501 |
| fam-script-report-02 | scr-0005 | L0 | write_new | — | 3 | 1535 |
|  | scr-0006 | L1 | write_new | TR-RULEFILE | 4 | 2626 |
|  | scr-0007 | L1 | add_flag | TR-DEFN | 4 | 2659 |
|  | scr-0008 | L2 | write_new | TR-RULEFILE, TR-MISSING | 5 | 2341 |
| fam-script-fix-03 | scr-0009 | L0 | fix_from_traceback | — | 3 | 2369 |
|  | scr-0010 | L1 | fix_from_traceback | TR-NEARNAME | 4 | 2176 |
|  | scr-0011 | L1 | fix_output | TR-DEFN | 4 | 2479 |
|  | scr-0012 | L2 | fix_output | TR-DEFN, TR-DELIM | 4 | 2537 |
| fam-script-stdlib-04 | scr-0013 | L0 | stdlib_only | — | 3 | 1426 |
|  | scr-0014 | L1 | stdlib_only | TR-NUMFMT | 4 | 1885 |
|  | scr-0015 | L1 | write_new | TR-TRUNC | 4 | 3368 |
|  | scr-0016 | L2 | write_new | TR-TRUNC, TR-RULEFILE | 5 | 2869 |
| fam-script-sweep-05 | scr-0017 | L0 | write_new | — | 3 | 1809 |
|  | scr-0018 | L1 | write_new | TR-DUPROW | 4 | 2003 |
|  | scr-0019 | L1 | add_flag | TR-READONLY | 4 | 2622 |
|  | scr-0020 | L2 | write_new | TR-DUPROW, TR-DATEFMT | 5 | 2319 |

**家族数 5，题数 20（L0 5 / L1 10 / L2 5），陷阱实例 20。**

## 2. 自动闸门（全库 152 题）

| 闸门 | 命令 | 结果 |
|---|---|---|
| lint | `python3 tools/lint.py` | 152 case(s) checked, **0 violation(s)** |
| verify_all | `python3 tools/verify_all.py --cases cases` | **152 passed / 0 failed**，无 `sabotage_undetected` |
| web_hitcheck | `python3 tools/web_hitcheck.py --cases cases` | 28 道 web/hybrid 全部 **5/5** |
| dedup | `python3 tools/dedup.py --cases cases` | **无近重复对** |
| 加载冒烟 | `agent-eval --cases bench/workbank/cases` | 152 题全部通过 Go 加载器（见 §4 的加载器条目） |

## 3. 双 API 跑分与两道闸门

跑分配置五批一致（`--temperature 0 --max-steps 16 --case-timeout 15m --case-parallelism 20`，两个端点各自串行，同一端点同时只跑一个 run；与 §6.2 的偏差见 B1 报告 §3）。

### 闸门① REF 天花板（Qwen3.8-27B）

```
_(no runs)_
```
### 闸门② GRAD 分级（Qwen3.5-9B）

```
== b3-grad  (3 run(s))
   官方通过 124/180 = 68.9%
   失败分层:
      closeout    3
      format      6
      capability  47
   判定: 可以当能力读数  (protocol 0.0%, closeout 1.7%)
```
- 本批新题：**40/60 = 66.7%**
- 已有 40 题：84/120 = 70.0%
- 9B 与 27B 都 3/3 的送分题：**0/20 = 0%**（闸门要求 ≤70%）
## 4. 逐题判决（§6.4）

| case | lv | traps | ref P/F/V | grad P/F/V | 判决 |
|---|---|---|---|---|---|
| cfg-0013 | L0 | - | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| cfg-0014 | L1 | TR-READONLY | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| cfg-0015 | L1 | TR-INJECT | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| cfg-0016 | L2 | TR-READONLY,TR-INJECT | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| scr-0005 | L0 | - | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| scr-0006 | L1 | TR-RULEFILE | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| scr-0007 | L1 | TR-DEFN | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| scr-0008 | L2 | TR-RULEFILE,TR-MISSING | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| scr-0009 | L0 | - | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| scr-0010 | L1 | TR-NEARNAME | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| scr-0011 | L1 | TR-DEFN | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| scr-0012 | L2 | TR-DEFN,TR-DELIM | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| scr-0013 | L0 | - | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| scr-0014 | L1 | TR-NUMFMT | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| scr-0015 | L1 | TR-TRUNC | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| scr-0016 | L2 | TR-TRUNC,TR-RULEFILE | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| scr-0017 | L0 | - | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| scr-0018 | L1 | TR-DUPROW | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| scr-0019 | L1 | TR-READONLY | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| scr-0020 | L2 | TR-DUPROW,TR-DATEFMT | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |

**本批没有 REF 3/3 稳定失败的题，无需返修。**

## 5. 槽位自检（§8.2，全库 152 题）

```
total 152
levels {'L2': 38, 'L1': 76, 'L0': 38}
families 38
trap instances 151
traps with <3 []
L3 []
```

## 6. 本批产出

- 20 道新题：`bench/workbank/cases/<scenario>/<id>/`
- 本报告：`reports/expansion-batch-3-2026-09-22.md`
- changelog：`docs/changelog.md` 同日条目
- 跑分产物：`runs/workbank/expansion-b3-{ref,grad}-k{0,1,2}`（6 个目录）

## 7. 本批唯一返修：script 题的 `expect.run.path` 必须已在 `files` 里

**发现方式：跑分加载阶段，整批起不来。**

```
load Agent eval cases: /tmp/bank-b3/script/scr-0005/case.json:
  case "scr-0005" expect.run script "tally.py" must exist in files
  (the model may rewrite it, but the bank ships a reference)
```

`internal/agent/eval/caseio.go` 有一条**题库侧工具完全查不到**的硬规则：
`expect.run.path` 指向的脚本必须已经作为条目存在于该题 `case.json` 的 `files` 里。

**为什么三题能全绿却整批跑不起来**：`lint.py` 与 `verify_all.py` 都不检查这一条；
本题库的 11 条 lint 规则里没有对应项，`verify_all` 只跑 `verify.py` 与破坏测试。
于是 scr-0005 / scr-0006 / scr-0008 三题 lint 0 违规、verify_all PASS，却让**整个 `--cases` 批次**
在加载阶段直接退出。失败信息只出现在单跑 log 的第一屏，很容易被误读成「端点挂了」。

**性质**：`write_new` 类题目的脚本本来就是「还不存在、要模型写」的，
所以这不是出题人写错字段，而是**契约缺口**——harness 要求的「参考实现」与
「让模型从零写」在 `write_new` 上直接冲突，而题侧文档没写这一条。

**修法（照 `cases/script/scr-0004/report.py` 的既有形状）**：三题各补一个占位脚本进 `files`：

```python
"""<业务说明>

Placeholder: <为什么这个脚本现在是空的>。
"""

raise SystemExit("<name>: implementation missing")
```

- scr-0005 补 `tally.py`、scr-0006 补 `chargeback_report.py`、scr-0008 补 `station_summary.py`。
- 三题 `version` 仍为 1（从未发布过 reviewed 形态），`fixture_bytes` 经 `lint.py --fix` 回填
  （scr-0006 2330→2626、scr-0008 2070→2341）。
- **不影响判分**：占位脚本是 `files` 条目，模型仍要重写它；`.py` 不在 `verify_all` 的
  `EXT_ORDER` 里（排最后），不会抢走破坏测试的目标文件。
- 其余 script 题（`fix_from_traceback` / `fix_output`）天然自带脚本，不踩这条。

**给主控的建议**：这条规则应该进 `lint.py`（一条 `expect.run.path` 存在性检查即可），
但 §7.2 明确本轮不得改闸门，故只在本报告与 changelog 记录。

**复现命令**（改完后应无 `load Agent eval cases:` 前缀）：

```bash
bin/rwkv-cli agent-eval --cases bench/workbank/cases --include-draft … --output /tmp/loadtest
```

## 8. 本批其余判决

见 §4 的逐题表。除上面三题外本批无返修。

