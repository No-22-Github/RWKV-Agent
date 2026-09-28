# workbank 扩量批次报告 — B4（2026-09-22）

> 本轮把题库从 40 扩到 152（新增 112）。B4 是 5 个批次中的第 4 批，含 5 个家族 / 20 道新题。
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
| fam-hyb-deps-02 | hyb-0005 | L0 | web_then_edit | — | 3 | 572 |
|  | hyb-0006 | L1 | local_first | TR-NOTOOLNEED | 3 | 609 |
|  | hyb-0007 | L1 | web_then_edit | TR-SUPERSEDE | 4 | 509 |
|  | hyb-0008 | L2 | web_then_edit | TR-SUPERSEDE, TR-READONLY | 5 | 670 |
| fam-hyb-tax-03 | hyb-0009 | L0 | web_then_calc | — | 3 | 631 |
|  | hyb-0010 | L1 | web_then_calc | TR-DIRMAP | 4 | 985 |
|  | hyb-0011 | L1 | multi_turn | TR-AMBIG | 4 | 576 |
|  | hyb-0012 | L2 | web_then_calc | TR-DIRMAP, TR-RULEFILE | 5 | 952 |
| fam-web-deprecation-02 | web-0005 | L0 | deprecation | — | 3 | 0 |
|  | web-0006 | L1 | deprecation | TR-SUPERSEDE | 4 | 0 |
|  | web-0007 | L1 | deprecation | TR-SNIPPETVAGUE | 4 | 0 |
|  | web-0008 | L2 | deprecation | TR-SUPERSEDE, TR-SNIPPETVAGUE | 5 | 0 |
| fam-web-errmsg-03 | web-0009 | L0 | error_meaning | — | 3 | 0 |
|  | web-0010 | L1 | error_meaning | TR-FETCHFAIL | 4 | 0 |
|  | web-0011 | L1 | error_meaning | TR-EARLYHIT | 2 | 0 |
|  | web-0012 | L2 | error_meaning | TR-FETCHFAIL, TR-DECOY | 5 | 0 |
| fam-web-version-04 | web-0013 | L0 | lookup_value | — | 3 | 0 |
|  | web-0014 | L1 | latest_version | TR-EARLYHIT | 2 | 0 |
|  | web-0015 | L1 | lookup_value | TR-LONG | 3 | 0 |
|  | web-0016 | L2 | latest_version | TR-EARLYHIT, TR-WEBSTALE | 5 | 0 |

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
== b4-grad  (3 run(s))
   官方通过 106/180 = 58.9%
   失败分层:
      closeout    2
      format      3
      capability  69
   判定: 可以当能力读数  (protocol 0.0%, closeout 1.1%)
```
- 本批新题：**27/60 = 45.0%**
- 已有 40 题：79/120 = 65.8%
- 9B 与 27B 都 3/3 的送分题：**0/20 = 0%**（闸门要求 ≤70%）
## 4. 逐题判决（§6.4）

| case | lv | traps | ref P/F/V | grad P/F/V | 判决 |
|---|---|---|---|---|---|
| hyb-0005 | L0 | - | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| hyb-0006 | L1 | TR-NOTOOLNEED | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| hyb-0007 | L1 | TR-SUPERSEDE | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| hyb-0008 | L2 | TR-SUPERSEDE,TR-READONLY | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| hyb-0009 | L0 | - | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| hyb-0010 | L1 | TR-DIRMAP | 0/0/0 | 1/2/0 | 抖动（记报告不改题） |
| hyb-0011 | L1 | TR-AMBIG | 0/0/0 | 1/2/0 | 抖动（记报告不改题） |
| hyb-0012 | L2 | TR-DIRMAP,TR-RULEFILE | 0/0/0 | 1/2/0 | 抖动（记报告不改题） |
| web-0005 | L0 | - | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| web-0006 | L1 | TR-SUPERSEDE | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| web-0007 | L1 | TR-SNIPPETVAGUE | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| web-0008 | L2 | TR-SUPERSEDE,TR-SNIPPETVAGUE | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| web-0009 | L0 | - | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| web-0010 | L1 | TR-FETCHFAIL | 0/0/0 | 2/1/0 | 抖动（记报告不改题） |
| web-0011 | L1 | TR-EARLYHIT | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| web-0012 | L2 | TR-FETCHFAIL,TR-DECOY | 0/0/0 | 1/2/0 | 抖动（记报告不改题） |
| web-0013 | L0 | - | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| web-0014 | L1 | TR-EARLYHIT | 0/0/0 | 3/0/0 | 抖动（记报告不改题） |
| web-0015 | L1 | TR-LONG | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |
| web-0016 | L2 | TR-EARLYHIT,TR-WEBSTALE | 0/0/0 | 0/3/0 | 抖动（记报告不改题） |

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
- 本报告：`reports/expansion-batch-4-2026-09-22.md`
- changelog：`docs/changelog.md` 同日条目
- 跑分产物：`runs/workbank/expansion-b4-{ref,grad}-k{0,1,2}`（6 个目录）

## 7. 本批的契约观察

### 7.1 `web/recordings/` 在仓库里不存在（文档空洞）

规格书 §3.6 与手册 §9.2 第 13 条都要求 web fixture「从 `web/recordings/` 的真实 Brave / Tavily
响应改写，不手写整条结果」。**该目录在本仓库中不存在**（`find . -type d -name recordings` 无结果，
全库仅 `HANDOFF.md` / `expansion-152-handoff.md` 两处引用它）。

本批的处理：按**可观察的形状**改写——照已发布且过审的 `cases/web/web-0002/case.json` 的
fixture 形状写（`query_match` / `url` / `url_match` / `title` / `snippet` / `content` / `published_at`），
不复制任何既有页面的文本，每个产品/页面都另起。**建议主控**：要么补上 `web/recordings/`，
要么把这条要求从两份文档里删掉——否则每个起草 Agent 都要自己决定怎么绕过它。

### 7.2 `expect.max_calls` 是 **case 级**，不是 turn 级

`expect.max_calls` 挂在 `CaseExpect`（`internal/agent/eval/types.go:63`、`expectcheck.go`），
turn 级的同名键会被**静默忽略**。TR-EARLYHIT 的四道题（web-0011、web-0014、web-0016）
都写在 `case.expect.max_calls`。手册 §4.2 的速查表把它列在「turn 级 expect」一栏，**是错的**。

### 7.3 TR-FETCHFAIL 的 fixture 形状

「首链失效」在 fixture 里表现为：该条目**有 `url` 但故意不给 `url_match`**（或给的 `url_match`
不是自身 url 的子串），于是 `web_fetch` 取不到、返回固定 not-found 页。
`web_hitcheck.py` 对这类条目会打 warning 而不是 fail——**这个 warning 就是 TR-FETCHFAIL 的正确形状**，
不是缺陷。本批 web-0010 / web-0012 各有一条这样的 warning。
（lint 的 `web_fixture.url_match` 闸门只查「url_match 能否解析回自己」，没写 url_match 的条目直接跳过，
所以两者不冲突。）

### 7.4 `output_contains` 与 `verify_all` 的形状匹配

`verify_all.matches_expectation` 只识别 `expected_number` / `output_equals(_any)` / `expect.files` 三种形状，
**不收集 `output_contains`**。于是「用 `output_contains` 判分的题，其 verify.py 只能打印一个不被识别的键」，
`verify_all` 记 `verify_shape_unknown` 警告（`ok: true`，不是失败），
且它的破坏测试因为没有可比对的期望而**结构性空转**。
已发布的 `code-0002` / `fs-0004` / `nt-0003` 都是这个形状，本批沿用。
受影响的本批题：web-0009/0010/0011/0012（error_meaning 收敛成一个自造词）。这是判分侧口径问题，
按 §1.2 记在这里，不动 scorer。

