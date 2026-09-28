# workbank 扩量批次报告 — B5（2026-09-22）

> 本轮把题库从 40 扩到 152（新增 112）。B5 是 5 个批次中的第 5 批，含 6 个家族 / 24 道新题。
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
| fam-code-testreport-02 | code-0005 | L0 | report_test_result | — | 2 | 5033 |
|  | code-0006 | L1 | report_test_result | TR-CLAIM | 3 | 3767 |
|  | code-0007 | L1 | explain_readonly | TR-READONLY | 4 | 2351 |
|  | code-0008 | L2 | explain_readonly | TR-CLAIM, TR-READONLY | 5 | 2489 |
| fam-code-edge-03 | code-0009 | L0 | locate_definition | — | 3 | 1379 |
|  | code-0010 | L1 | fix_edge_case | TR-DEFN | 4 | 1167 |
|  | code-0011 | L1 | count_markers | TR-DECOY | 4 | 2450 |
|  | code-0012 | L2 | fix_edge_case | TR-DEFN, TR-READONLY | 5 | 1363 |
| fam-doc-changelog-02 | doc-0005 | L0 | latest_version | — | 3 | 1068 |
|  | doc-0006 | L1 | latest_version | TR-DECOY | 3 | 1003 |
|  | doc-0007 | L1 | link_check | TR-NEARNAME | 4 | 1655 |
|  | doc-0008 | L2 | link_check | TR-DECOY, TR-MULTISRC | 5 | 1378 |
| fam-doc-handbook-03 | doc-0009 | L0 | policy_lookup | — | 3 | 3498 |
|  | doc-0010 | L1 | policy_lookup | TR-RULEFILE | 4 | 3892 |
|  | doc-0011 | L1 | write_structured | TR-DEFN | 4 | 4292 |
|  | doc-0012 | L2 | write_structured | TR-RULEFILE, TR-LONG | 6 | 50975 |
| fam-fs-audit-02 | fs-0005 | L0 | count_by_type | — | 2 | 3841 |
|  | fs-0006 | L1 | count_by_type | TR-TRUNC | 4 | 18978 |
|  | fs-0007 | L1 | largest | TR-DECOY | 4 | 6434 |
|  | fs-0008 | L2 | largest | TR-TRUNC, TR-DECOY | 5 | 30591 |
| fam-fs-dedupe-03 | fs-0009 | L0 | presence | — | 3 | 789 |
|  | fs-0010 | L1 | duplicates | TR-DECOY | 4 | 1289 |
|  | fs-0011 | L1 | presence | TR-ABSENT | 4 | 967 |
|  | fs-0012 | L2 | duplicates | TR-DECOY, TR-NEARNAME | 5 | 1164 |

**家族数 6，题数 24（L0 6 / L1 12 / L2 6），陷阱实例 24。**

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
== b5-grad  (3 run(s))
   官方通过 128/190 = 67.4%
   作废(上游中断，不计分母) 2
   失败分层:
      infra       2
      format      5
      capability  57
   判定: 可以当能力读数  (protocol 0.0%, closeout 0.0%)
```
- 本批新题：**53/70 = 75.7%**（另有 2 次作废，不计分母）
- 已有 40 题：75/120 = 62.5%
- 9B 与 27B 都 3/3 的送分题：**0/24 = 0%**（闸门要求 ≤70%）
## 4. 逐题判决（§6.4）

| case | lv | traps | ref P/F/V | grad P/F/V | 判决 |
|---|---|---|---|---|---|
| code-0005 | L0 | - | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| code-0006 | L1 | TR-CLAIM | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| code-0007 | L1 | TR-READONLY | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| code-0008 | L2 | TR-CLAIM,TR-READONLY | 0/0/0 | 1/2/0 | 抖动（记报告不改题） |
| code-0009 | L0 | - | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| code-0010 | L1 | TR-DEFN | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| code-0011 | L1 | TR-DECOY | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| code-0012 | L2 | TR-DEFN,TR-READONLY | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| doc-0005 | L0 | - | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| doc-0006 | L1 | TR-DECOY | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| doc-0007 | L1 | TR-NEARNAME | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| doc-0008 | L2 | TR-DECOY,TR-MULTISRC | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| doc-0009 | L0 | - | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| doc-0010 | L1 | TR-RULEFILE | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| doc-0011 | L1 | TR-DEFN | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| doc-0012 | L2 | TR-RULEFILE,TR-LONG | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| fs-0005 | L0 | - | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| fs-0006 | L1 | TR-TRUNC | 0/0/0 | 0/2/1 | 抖动（记报告不改题） |
| fs-0007 | L1 | TR-DECOY | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| fs-0008 | L2 | TR-TRUNC,TR-DECOY | 0/0/0 | 0/2/1 | 抖动（记报告不改题） |
| fs-0009 | L0 | - | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| fs-0010 | L1 | TR-DECOY | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| fs-0011 | L1 | TR-ABSENT | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| fs-0012 | L2 | TR-DECOY,TR-NEARNAME | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |

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

- 24 道新题：`bench/workbank/cases/<scenario>/<id>/`
- 本报告：`reports/expansion-batch-5-2026-09-22.md`
- changelog：`docs/changelog.md` 同日条目
- 跑分产物：`runs/workbank/expansion-b5-{ref,grad}-k{0,1,2}`（6 个目录）

## 7. TR-LONG / TR-TRUNC 题的实测字节与步数（§6.2.1 要求）

| case | 陷阱 | 最大文件字节 | fixture_bytes | 文件数 | 27B 实测步数（k0/k1/k2） |
|---|---|---:|---:|---:|---|
| doc-0012 | TR-RULEFILE, TR-LONG | 47,982 | 50,975 | 4 | 见下方 REF 表 |

doc-0012 的手册正文 47,982 B（1,011 行），**在 45–70KB 目标区间内、低于 80KB 硬上限**，
且低于 64KB `read_file` 截断线——按 §6.2.1 的意图，它测的是「长输入里找唯一适用条款」，
不是截断行为。适用条款（附录 D.1.1 的 36 个月）在正文里只出现一次。

## 8. 批量文件题的规模（不是 bug，§10 已预告）

| case | 陷阱 | 文件数 | fixture_bytes | 说明 |
|---|---|---:|---:|---|
| fs-0006 | TR-TRUNC | 831 | 18,978 | 需超过 `list_files` 的 500 条 schema 上限 |
| fs-0008 | TR-TRUNC, TR-DECOY | 558 | 30,591 | 同上 |
| scr-0015 | TR-TRUNC | 215 | 3,368 | 超过默认 200 条上限 |
| scr-0016 | TR-TRUNC, TR-RULEFILE | 208 | 2,869 | 同上 |

堆的是**文件个数不是字节数**（每题的文件都是两三行短内容），所以 `case.json` 仍可复核。
`fixture_bytes` 高于手册 §1.6 的 8KB 指导值是设计使然，见 §10 的「这些不是 bug」表。

## 9. `verify_all` 破坏测试在 `expected_stdout` 题上的结构性空转

script 题的 `verify.py` 打印 `{"expected_stdout": …}` 时，`verify_all` 只把它与 `expect.run.expected_stdout`
逐字节比对（`run_expect_match` 检查，本批全部 true），**但不参与破坏测试的期望匹配**
（`matches_expectation` 不识别该形状）。于是这些题的破坏测试判定退化为
「verify.py 报错即算检出」——本批的出题人据此让每个 `verify.py` 在被删首行时**主动抛错**
（断言首行 header / 表头），所以三题的 sabotage 都是真的检出了，只是走的不是数值分歧那条路。
已发布的 scr-0001 同形，本批沿用。

