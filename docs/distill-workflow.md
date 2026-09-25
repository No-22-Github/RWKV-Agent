# 蒸馏数据工作流 —— 实施规格书

> 读者：在独立 Agent 环境里执行本流程的**主控 Agent**，以及它派出的**起草子 Agent**（子 Agent 只需读 §2 和 §2.7 的简报）。
> 文中「必须 / 不得」是硬约束，每条都附了理由；理由看不懂就停下来问人，**不要当成可优化项绕过去**。
> 核心章节是 **§2（题怎么出）** 和 **§3（每一步的命令与闸门）**。工具在 §4 有两处前置改造，是**阻塞项**。
>
> 写于 2026-09-25，基于 main `868f332` 加上同日修复的 `lint --fix` bug（见 §4.0）。
> 管线各环节已在本机冒烟：`corpus paths` → `corpus render` 在 workbank 上 26/26 通过；
> 用 §2.5 的样例题在非 workbank 目录上 render，正确路径出行、错误路径（答 decoy）被拒，`wire_hash` 与 g1k 跑分一致。
> 同日真实老师冒烟：`bench/distill/cases/notool/nt-5001..5005`（5 道闲聊直答题）在 Qwen3.8-27B 上跑 k=2 → 4 条路径 → 4 行，0 拒绝，
> `wire_hash` 一致；暴露两个问题，都已写进本文：闲聊题与 lint 规则冲突（§4.3）、API 调用需要 build tag（§3 S0）。

## 0. 目标

批量产出**只用于训练**的 Agent 轨迹数据：自己出题（`bench/distill`）→ 让强模型（DeepSeek-flash）当老师在真实 harness 里做题 →
从老师的**通过**轨迹里只取动作（工具调用 + 终答）→ 在 student 的 wire（g1k）下**重放**并切成训练行。

最关键的取舍：**训练行的字节不由我们拼，由 eval harness 重放产生。** 所以训练时模型看到的 prompt 与跑分时逐字节相同
（System 块、工具回执、post-tool 提醒、失败提示全部来自同一份 Go 代码）。代价是：题必须写成 harness 能加载、能判分的 bank 格式，
判分器就是数据的质检员——**判据错一题，数据就错一题**。

## 1. 总览

### 1.1 流水线

```
S1 起草 ──► S2 静态闸门 ──► S3 去污染 ──► S4 老师跑 k=3 ──► S5 抽路径 + pass@k 质检 ──► S6 重放切行 ──► S7 批次验收 ──► S8 打包数据集
(子Agent)  lint/verify/     decontam      agent-eval        corpus paths               corpus render      抽检+报告        corpus pack
           dedup/hitcheck   (vs 测试集)    (chat-completions)                          (g1k, 无需模型)                     (§4.2 新增)
```

一批（batch）走完整条线再开下一批。第一批 200 题，编号 `b01`。

### 1.2 目录

| 路径 | 内容 | 入库 |
|---|---|---|
| `bench/distill/cases/<scenario>/<id>/` | 题目：`case.json` + `verify.py` + `NOTES.md` | 是 |
| `bench/distill/cases-shelved/<scenario>/<id>/` | 老师 0/3 且确认不是题目缺陷的题（留档不删） | 是 |
| `bench/distill/batches.jsonl` | 每批一行：批号、题 ID 列表、起草模型、老师模型与参数、commit | 是 |
| `bench/distill/exclude.jsonl` | 抽检剔除的路径：`{"case_id":"tab-5003--p1","reason":"…","batch":"b01"}` | 是 |
| `bench/distill/scripts/<batch>.jsonl` | `corpus paths` 的产物（老师动作脚本） | **待用户决定**，见 §8 |
| `bench/distill/reports/<batch>.md` | 批次报告（§3 S7） | 是 |
| `runs/distill/<batch>/…` | 老师 run、render 产物、rows | 否（`runs/` 已 gitignore） |
| `runs/distill/dataset-YYYYMMDD/` | 最终训练集 | 否 |

### 1.3 不做什么

- **不改写测试题当种子。** 700 条旧语料的 36 个种子全是 workbank 题，整族泄漏，改写后的变体表面相似度低、decontam 查不出来。只能从来源上堵，见 §2.1。
- **不用 `datasets/…/tooling/workv1_wire.py` 或任何手写拼接。** 它漏掉了 harness 在两步之间插入的 User 块。训练行只能来自 `corpus render`。
- **不出中文题（本期）。** 阻塞原因：`corpus decontam` 还不支持 CJK（方案已提，未实现）；出题规范与答案契约都是英文。中文是下一期。
- **不筛老师自报的身份。** 老师回答「I'm Qwen / I'm DeepSeek」照常收，不加排除词、不加打包闸门、不在抽检时因此剔除。这是用户的决定：RWKV 基模被问身份时本来就大概率自称 DeepSeek，筛掉这类数据没有意义。身份类题目的判据只要求回答了身份问题（如 `output_contains_any` 含 `assistant`、`model`、`AI`），不管说的是哪家。
- **不做人工终审、不把题升为 `reviewed`。** 蒸馏题永远是 `draft`，质检靠老师 pass@k + 判分器 + 抽检。
- **不对 student 跑分，也不按 student 难度加权**（本期不做）。

## 2. 蒸馏题（核心章节）

出题规范**沿用 workbank 全套**，以下三份是最高权威，起草前必须通读：

- `bench/workbank/docs/authoring-guide.md`：题型清单 §2、陷阱目录 §3、难度规则 §4、tag 词表 §5、表面多样性 §6、NOTES 格式 §7、反例库 §8（X-001～X-012 每条都是真实翻过车的）
- `bench/workbank/docs/HANDOFF.md` §2：`case.json` schema v5 的字段契约与完整样例
- `bench/workbank/docs/M0-findings.md` §1/§2/§9：工具的真实行为（`data_query` 不解析 `$1,234.50`、`read_file` 64KB 截断等）

机器可读枚举：`bench/workbank/docs/tag-vocab.json`（**只读引用，不复制**。复制会让两份词表漂移，而 lint 按词表判合法）。

本节只写**蒸馏题与测试题不同的地方**。

### 2.1 来源规则（主闸门）

| 起草子 Agent **可以读** | **不得读** |
|---|---|
| 上面三份文档、`tag-vocab.json` | `bench/workbank/cases/`、`bench/workbank/cases-shelved/` 下任何文件 |
| 格式样例：本文 §2.5；`bench/workbank/tools/testdata/tabular/tab-9001/`、`…/web/web-9001/` | `bench/workbank/reports/`、`bench/workbank/ledger/`（里面引用了题面与答案） |
| 已入库的 `bench/distill/cases/`（查重、避免撞名） | `runs/` 下任何 trace（跑的都是测试题）；`datasets/workspace-agent-700-20260920/`（workbank 种子题的变体） |

理由：decontam 只能按表面文本比对（prompt 5-gram、fixture 行、专有名），「换名换数、同一骨架」的变体会漏过去。
不读测试题就不可能写出测试题的变体。authoring-guide 反例库里出现的题目片段（X-004 的汇率题等）也**不得**作为骨架。

### 2.2 目录、ID、标记

| 项 | 规定 | 理由 |
|---|---|---|
| 目录 | `bench/distill/cases/<scenario>/<id>/`，scenario 用全名（`tabular`、`notool`…） | lint 的 `dir_structure` 规则要求 `<scenario>/<id>/` 两层 |
| ID | `<abbrev>-<4位数>`，**从 5001 起**，按场景各自递增，跨批次连续（b01 用 `tab-5001`…`tab-5024`，b02 从 `tab-5025` 接着编） | lint 的正则是 `^[a-z]+-\d{4}$`；workbank 用 0001–0999、样例用 9001，5001 起不会撞号。撞号会让 `paths` 输出的 `tab-0001--p1` 与测试题 ID 混淆 |
| abbrev | `tab log cfg doc fs scr code web hyb nt`（见 `tag-vocab.json` 的 `scenarios`） | lint 校验前缀与 scenario 一致 |
| canary | `description` 以 ` DISTILL-CANARY-<8位小写hex>` 结尾，每题不同；`verify.py` 首行注释写同一串 | **不得用 `WORKBANK-CANARY`**：那串的含义是「测试题，禁止进训练语料」，蒸馏题带它会让下游的泄漏扫描误报，或者更糟，让人习惯性地忽略它。需要 §4.1 的 lint 改造 |
| `tags.author` | `llm:<起草模型名>`，如 `llm:glm-4.7-distill` | lint 规定 `llm:` 作者只能配 `status: draft` |
| `tags.status` | 永远 `draft` | 同上；`--include-draft` 让 agent-eval 加载它们 |
| `tags.reviewer` | `null` | 无人审 |
| `family` | `fam-<abbrev>-<slug>-NN`，slug 不得与 workbank 已有 family 同名（主控用 `grep -rho '"family": "[^"]*"' bench/workbank/cases` 生成黑名单发给子 Agent，**只发名字，不发题**） | family 同名会误导以后的归因 |

### 2.3 与 workbank 出题规范的差异

| 规则 | workbank | distill | 理由 |
|---|---|---|---|
| 家族大小 | 4 题一套（L0→L1→L1→L2） | **每族 ≤ 3 题** | 蒸馏要多样性；同骨架题太多，数据里就是同一条轨迹换数字 |
| 难度配比 | L0 25% / L1 50% / L2 25% | **L0 35% / L1 45% / L2 20% / L3 0%** | student 的头号死因是该收尾不收尾（09-17 失败归因：重复调用→强制收尾→复读 13/37），短而干净的轨迹最能教收尾 |
| `script` 题的 `ref_calls` | 不限 | **≤ 8** | DeepSeek 在长脚本题上会把 16 步用光被强制收尾（dsflash 报告 scr-0012/0016/0020），`paths` 会丢弃所有强制收尾路径，出了也拿不到数据 |
| 宽松判据 | `output_contains_any` 词表（如 `["?","which",…]`） | 允许，但这类题的所有路径必须在 S7 **逐条抽检** | 判据宽松 = 质检宽松。「答了个问号就算反问」在测试里可以接受，在训练数据里会教坏 |
| 答案值的字面量 | 无规定 | 正确答案的数值**不得**作为巧合字面量出现在与答案无关的字段里 | `bank verify` 的破坏测试会找到 fixture 里第一个等于答案的数并 +1。若那个数与答案无关，verify.py 结果不变，报 `sabotage_undetected`（本文样例初稿就踩了：答案 5，恰好某行 parcels=5） |
| 其余 | — | 完全相同 | 题面禁工具名/步骤/陷阱禁词、答案契约逐字节、`trap_decoys` ≠ 正确答案、verify.py 只用标准库且从 files 独立计算、NOTES 四段、英文出题 |

### 2.4 第一批配额（b01，200 题）

> **已被 [distill-allocation-v1.md](distill-allocation-v1.md) 取代**（在 700 条基础上加约 650 题，分 3 批）。下表只作为最初的设计记录保留。

| scenario | 题数 | task_type 侧重（数字为至少题数） | 说明 |
|---|---|---|---|
| tabular | 24 | aggregate 5、filter_count 5、reconcile 4、policy_calc 4、join 3、rank 3 | 其中 ≥ 6 题的主表 ≥ 40 行，让 `data_query` 比读全文更划算 |
| logs | 20 | locate_error 5、count_events 5、time_window 4、aggregate_jsonl 3、root_cause 3 | |
| config | 18 | read_effective 5、precedence 4、edit_value 4、missing_keys 3、merge 2 | |
| docs | 16 | policy_lookup 5、extract_items 4、latest_version 3、write_structured 2、link_check 2 | |
| filesystem | 14 | find_file 4、count_by_type 4、largest 3、duplicates 2、presence 1 | |
| script | 16 | write_new 5、fix_from_traceback 4、add_flag 3、fix_output 2、stdlib_only 2 | `ref_calls` ≤ 8（§2.3） |
| code | 16 | locate_definition 4、find_callers 4、report_test_result 3、fix_edge_case 3、explain_readonly 2 | fixture 必须是可解析的代码（反例 X-010） |
| web | 20 | lookup_value 6、latest_version 5、error_meaning 5、deprecation 4 | 其中 ≥ 4 题带 TR-EARLYHIT + `max_calls`（教「查到就停」） |
| hybrid | 16 | web_then_calc 5、web_then_edit 4、local_first 3、multi_turn 4 | multi_turn 4 题全部带 TR-AMBIG |
| notool | 40 | concept 8、unit_convert 6、snippet_in_reply 6、stable_fact 5、ambiguous_request 5、beyond_capability 5、**smalltalk 5** | smalltalk = 问候、道谢、「你是谁」「你能做什么」「你有哪些工具」，需要 §4.3；样例为 `nt-5001..5005` |
| **合计** | **200** | | |

**跨场景的行为指标**（按 tags 统计，S2 结束时由主控核对，不达标就补题）：

| 行为 | 至少 | 理由 |
|---|---|---|
| 单轮、零工具调用即可答（notool 除 ambiguous_request） | 35 题 | 2026-09-23 的 state LR 扫描：训练集首动作 100% 是工具调用，bfcl 崩。**零调用行是必需品，不是边角料** |
| TR-ABSENT（期望 `UNKNOWN`），且同 family 有答案存在的姊妹题 | 10 题 | 教诚实弃权；没有姊妹题就会教成「动不动 UNKNOWN」 |
| TR-NOCAP | 8 题 | notool 5 + 其他场景 3（如要求删文件、发邮件的配置/日志题） |
| TR-AMBIG 多轮 | 8 题 | hybrid 4 + notool ambiguous_request 中 4 |
| L0 且 `ref_calls` ≤ 3 | 60 题 | 收尾训练，理由同 §2.3 |

### 2.5 完整样例（已跑过全部闸门）

`bench/distill/cases/tabular/tab-5001/`。在本机实测：lint 除 canary 规则（等 §4.1）外 0 违规；verify 期望比对与破坏测试均通过；dedup、decontam 0 命中；
render 正确路径出行，答 7（decoy）的路径被拒。

`case.json`：

```json
{
  "id": "tab-5001",
  "description": "Count August 2026 shipments to Canada in a warehouse export that repeats some rows. DISTILL-CANARY-3e9a07b5",
  "category": "tabular",
  "tags": {
    "scenario": "tabular",
    "task_type": "filter_count",
    "traps": ["TR-DUPROW"],
    "trap_decoys": {"TR-DUPROW": 7},
    "axes": ["OBS"],
    "level": "L1",
    "family": "fam-tab-harrowship-01",
    "ref_calls": 3,
    "fixture_bytes": 990,
    "status": "draft",
    "version": 1,
    "author": "llm:distill-drafter",
    "reviewer": null
  },
  "web_fixture": [],
  "files": {
    "exports/shipments_2026-08.csv": "shipment_id,ship_date,order_ref,destination_country,carrier,parcels\nHX-40211,2026-08-02,PO-88104,Canada,Purolator,2\nHX-40212,2026-08-03,PO-88107,United States,UPS,1\nHX-40213,2026-08-05,PO-88111,Canada,Canada Post,3\nHX-40214,2026-08-07,PO-88115,Mexico,DHL,1\nHX-40215,2026-08-11,PO-88120,Canada,Purolator,1\nHX-40216,2026-08-12,PO-88124,United States,FedEx,4\nHX-40215,2026-08-11,PO-88120,Canada,Purolator,1\nHX-40217,2026-08-18,PO-88131,Canada,Canada Post,2\nHX-40218,2026-08-21,PO-88136,United States,UPS,1\nHX-40219,2026-08-26,PO-88142,Canada,DHL,3\nHX-40217,2026-08-18,PO-88131,Canada,Canada Post,2\nHX-40220,2026-08-29,PO-88147,Mexico,DHL,2\nHX-40218,2026-08-21,PO-88136,United States,UPS,1\n",
    "README.md": "# Harrowgate Cycle Supply - outbound shipments\n\nNightly export from the warehouse system, August 2026.\nOne shipment per order. The export job retried twice this month, so some rows were written more than once.\n",
    "notes/carrier-contacts.txt": "Purolator account rep: Denise Arbour, ext 214\nCanada Post pickup window: 14:00-16:00 weekdays\n"
  },
  "turns": [
    {
      "prompt": "Harrowgate Cycle Supply needs the number of orders it shipped to Canada in August 2026 for the cross-border freight invoice. How many were there? Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.",
      "expect": {"expected_number": 5, "tolerance": 0.01}
    }
  ]
}
```

`verify.py`：

```python
# DISTILL-CANARY-3e9a07b5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/shipments_2026-08.csv"]))
orders = {r["order_ref"] for r in rows if r["destination_country"] == "Canada" and r["ship_date"].startswith("2026-08")}
print(json.dumps({"expected_number": len(orders)}))
```

`NOTES.md`：

```markdown
## Traps
- TR-DUPROW: exports/shipments_2026-08.csv repeats HX-40215 and HX-40217 (both Canada) and HX-40218 (United States). Counting Canada rows instead of orders gives 7.

## Reference solution
1. List the workspace to find the export and README.
2. Read README.md: the export job retried, so rows can repeat.
3. Read exports/shipments_2026-08.csv, keep Canada rows, count distinct order_ref: PO-88104, PO-88111, PO-88120, PO-88131, PO-88142 = 5.

## Why the answer is unique
The decoy 7 counts rows, but the question asks for orders and the README says there is one shipment per order, so the repeated rows are the same shipments written twice. Every repeated row matches its original in every column, so there is no reading in which they are separate orders. The answer is 5.
```

注意 `Why the answer is unique` 是在论证 **decoy 为什么错**，不是复述正确答案（反例 X-004）。

**其他题型的 `expect` 形状**（照抄 workbank 已验证的写法）：

| 题型 | 轮 | `expect` |
|---|---|---|
| notool 数值（概念/换算） | 1 | `{"expected_number": 429, "tolerance": 0.01, "tools": []}` |
| 越权拒绝（TR-NOCAP / beyond_capability） | 1 | `{"forbidden_tools": ["write_file","append_file","replace_lines"], "output_contains_any": ["cannot","Cannot","can't","Can't","unable","Unable","not able","Not able","do not have access","Do not have access","no access","No access"], "output_excludes": ["UNKNOWN"]}`——**不带答案契约**（§4.3.1）；判据里不得出现 `UNKNOWN` |
| 多轮反问（TR-AMBIG） | 1 | `{"tools": [], "output_contains_any": ["?","which","Which","specif","Specif","confirm","Confirm","clarif","Clarif","unclear","Unclear","ambiguous","Ambiguous","need to know","Need to know","need the","Need the"]}` |
| | 2 | 第二轮 prompt 给出澄清，`expect` 按普通数值/字符串题写 |
| 写文件 / 脚本 | case 级 | `"expect": {"files": {...}, "run": {...}}`，最后一轮 prompt 以 `When finished, reply DONE.` 结尾（HANDOFF §2.6） |

### 2.6 出题坑（本项目特有）

1. **写目录必须预先存在。** 题面要求写入的目录要在 `files` 里放一个 `.keep`，工作区工具不能建目录（lint `m0.write_dir`）。
2. **web 题的 `url_match` 不得互为前缀。** harness 取最长匹配，但 lint `web_fixture.url_match` 会查；每加一个页面就跑一次 lint（反例 X-008）。
3. **web 题的 `query_match` 要宽。** 老师自己拼搜索词，`query_match` 太窄时搜索返回空、老师 0/3。NOTES 里的五条改写查询必须 `bank hitcheck` 5/5。
4. **脚本题的 hidden 输入集必须在工作区内**（反例 X-006；lint `expect.run.hidden`）。
5. **题面语气也是题面。** 不用 quick / simple / just，也不用 carefully / note that（反例 X-009）。
6. **名字池。** 公司、人名、SKU 每批内不重复，并避开 §2.2 发给子 Agent 的 family 黑名单涉及的领域名；decontam 的 names 维度会查专有名重合。

### 2.7 起草子 Agent 简报模板

主控按场景派 10 个子 Agent（每个场景一个），每个子 Agent 收到的简报：

```
你为 RWKV-Agent 的蒸馏题库出题。场景：<scenario>；本批题数：<n>；ID 从 <abbrev>-<起始号> 连续编号；
task_type 配额：<§2.4 该行>；本场景要承担的行为指标：<§2.4 下表中分到本场景的份额>。

必读：docs/distill-workflow.md §2 全部；bench/workbank/docs/authoring-guide.md；bench/workbank/docs/HANDOFF.md §2；
bench/workbank/docs/M0-findings.md §1/§2/§9；bench/workbank/docs/tag-vocab.json。
禁读：bench/workbank/cases/、bench/workbank/cases-shelved/、bench/workbank/reports/、bench/workbank/ledger/、runs/。
禁用 family 名：<黑名单>。

每题写 bench/distill/cases/<scenario>/<id>/{case.json,verify.py,NOTES.md}。
自检（全部通过才算交付，在仓库根目录执行）：
  bin/rwkv-lab bank lint --fix --canary-prefix DISTILL-CANARY --cases bench/distill/cases   # 先回填 fixture_bytes
  bin/rwkv-lab bank lint --canary-prefix DISTILL-CANARY --case bench/distill/cases/<scenario>/<id>   # 每题 0 违规
  bin/rwkv-lab bank verify --cases bench/distill/cases/<scenario>                            # 全部 PASS，含 sabotage
  bin/rwkv-lab bank hitcheck --case <dir>                                                     # web/hyb 题 5/5
不要跑 git；不要碰别的场景目录；不要改工具代码。交付时列出每题的 ID、task_type、traps、level、正确答案。
```

## 3. 流水线逐步规格

下面命令都在仓库根目录执行。`B=b01` 表示批号。

### S0 环境（每批开工前）

```bash
git pull && go build -tags chatcompletions -o bin/rwkv-cli ./cmd/rwkv-cli && go build -o bin/rwkv-lab ./cmd/rwkv-lab
git rev-parse HEAD && git status --short          # 工作区必须干净
go test ./internal/lab/... ./internal/agent/eval/ # 必须全过
shasum -a 256 bin/rwkv-cli                        # 记入 batches.jsonl
```

- **`-tags chatcompletions` 必须带**：不带的二进制调老师时报 `Chat Completions support is not included in this build`。这个 tag 只加客户端，不改 wire，render 用同一个二进制没有问题（冒烟时 `wire_hash` 与不带 tag 的版本相同）。
- 老师的 API key 放环境变量，**不得写进任何文件**。agent-eval 默认读 `OPENAI_API_KEY`，可用 `--api-key-env <变量名>` 改。
- **本批从 S4 到 S8 不得重编 `bin/rwkv-cli`**。harness 一变，`wire_hash` 就变，同一批的 rows 会混进两种 wire。当前 g1k workbank 的 `wire_hash` 为
  `707c67403b1b2e5269ddfcd8ecee2bfb7ce4d8133912d102bc67f1324f8018cb`（harness `rwkv-agent-eval-v21`，scorer v3）。harness 升级后这个值会变，这是预期行为，见 §3 S8。

### S1 起草

按 §2.7 派 10 个子 Agent 并行起草。主控收齐后核对 §2.4 的两张表（题数、task_type 至少数、行为指标）；
`bin/rwkv-lab bank coverage --cases bench/distill/cases --summary` 可以打印场景 × 难度的填充表，**只看计数，不看它的配额列**（那是 workbank 的配额）。

### S2 静态闸门（主控对全批重跑一遍，不信子 Agent 的自检报告）

```bash
bin/rwkv-lab bank lint --canary-prefix DISTILL-CANARY --cases bench/distill/cases   # 退出码 0
bin/rwkv-lab bank verify --cases bench/distill/cases                                # 退出码 0
bin/rwkv-lab bank dedup --cases bench/distill/cases                                 # 无命中；有命中则改措辞或删一题
for d in bench/distill/cases/{web,hybrid}/*/; do bin/rwkv-lab bank hitcheck --case "$d"; done   # 每题 5/5
bin/rwkv-lab corpus loadcheck --cases bench/distill/cases                # 真 loader 预检（2026-09-25 加）
```

`verify` 的 `sabotage_undetected` **是硬失败，不是警告**（反例 X-011）。修法见 §2.3「答案值的字面量」。
`loadcheck` **是 S4 前的最后一道闸门**：lint 只看 tag 词表、verify 只跑脚本，两者都不查未知字段，而 agent-eval 的 loader 用 `DisallowUnknownFields`——b02 有一道题带了自写的 `answer_once` 字段，三轮老师跑当场全灭（`load Agent eval cases: decode … unknown field`），排查花了十几分钟。这一步 5 秒钟。

### S3 去污染

```bash
bin/rwkv-lab corpus decontam --test bench/workbank/cases        --candidates bench/distill/cases --report runs/distill/$B/decontam-cases.jsonl
bin/rwkv-lab corpus decontam --test bench/workbank/cases-shelved --candidates bench/distill/cases --report runs/distill/$B/decontam-shelved.jsonl
```

两条都必须 `0 flagged`（有命中时退出码 1）。命中的题**重写或删除**，不得调阈值。阈值是校准过的（旧 700 条的 anchor 36/36 命中、workbank 内部误报 0/148）。
下架题（cases-shelved）也要比：它们随时可能修好回到测试集。

### S4 老师跑 k=3

```bash
for k in 0 1 2; do
  bin/rwkv-cli agent-eval \
    --completion chat-completions --api-url "$TEACHER_URL" --model "$TEACHER_MODEL" \
    --chat-token-limit-field max-tokens \
    --temperature 0.3 --top-p 1 \
    --cases bench/distill/cases --include-draft \
    --tool-catalog work-v1 --file-tools lines \
    --max-steps 16 --max-tokens 4096 --decision-max-tokens 8192 \
    --case-parallelism 40 --case-timeout 30m \
    --output runs/distill/$B/teacher-k$k
done
```

| 参数 | 值 | 不许动的理由 |
|---|---|---|
| `--temperature` | 0.3 | **DeepSeek-flash 不能用 0**：T=0 五轮作废数 14→40，出现大量 UNKNOWN 早退和不调 web_search（`bench/workbank/reports/dsflash-baseline-2026-09-22.md` §2）。T=0.3 同时给出 k 次之间的路径多样性 |
| `--tool-catalog work-v1 --file-tools lines` | 固定 | 必须与 S6 render 的默认值一致。老师用了 student 没有的工具或参数形状，重放时会全部被拒 |
| `--max-steps 16` | 固定 | 与 student 预算相同。更长的老师路径在 student 预算下本来就不可复现 |
| `--decision-max-tokens 8192` | 固定 | dsflash 基线的设置；老师输出被截断会变成协议错误，白白浪费一次运行 |
| `--include-draft` | 必须 | 蒸馏题全是 draft，不加就一题都不加载 |
| 不传 `--profile` | — | API 模型走原生 chat；老师的 wire 不进训练数据（`paths` 只带走动作） |

- `$TEACHER_URL` / `$TEACHER_MODEL`：**待用户填写**（§8）。已知可用：
  - **自建 vLLM（2026-09-25 冒烟所用）**：`http://100.64.0.1:8000/v1/chat/completions` + `qwen3.8-27b`（Qwen3.8-27B-NVFP4，max_model_len 32768）。必须加 `--chat-thinking disabled`：它把 `chat_template_kwargs.enable_thinking=false` 发给 vLLM，否则 Qwen 的思考会占用输出预算。不需要 key，但 agent-eval 要求变量存在，传 `OPENAI_API_KEY=dummy`。并发先用 10，端点能力未测。
  - 官方 `https://api.deepseek.com/v1/chat/completions` + `deepseek-v4-flash`；中转 + `deepseek-flash`（dsflash 基线所用）。
- 每个 run 结束检查 `runs/distill/$B/teacher-k$k/summary.json`：infra 错误（超时、5xx）> 5% 就整轮重跑，换新的 `--output` 目录，**不得覆盖**。
- 单独补跑某几题：加 `--case <id>`（可重复），输出到 `teacher-fix-k$k`。

### S5 抽路径 + pass@k 质检

```bash
bin/rwkv-lab corpus paths \
  --run runs/distill/$B/teacher-k0 --run runs/distill/$B/teacher-k1 --run runs/distill/$B/teacher-k2 \
  --out runs/distill/$B/script.jsonl --report runs/distill/$B/paths.jsonl
```

`paths` 的丢弃规则（已实现，不要改）：失败、有协议重试、工具报错或被拒、进入强制收尾、终答被 harness 修复过。
选路规则：先取最短的，之后只收工具序列不同的，每题最多 2 条（`--max-per-case` 保持默认 2）；参数里等于默认值的项会被去掉。

**pass@3 分诊**（`paths` 会在 stderr 打印 `cases never passed`）：

| pass@3 | 处理 |
|---|---|
| 2/3、3/3 | 正常 |
| 1/3 | 正常，保留；只有通过的那条进数据 |
| 0/3 | 逐题看 trace 里老师的终答，对照 NOTES 的「Why the answer is unique」：<br>① 老师的答案是一种**站得住的读法** → 题目有歧义，改题（version+1，description / NOTES / verify.py 同一次改完，反例 X-007），对该题补跑 k=3，`paths` 时把旧 run 和补跑 run 一起传（旧轨迹会在 S6 按新题重判，不合的自动拒掉）；<br>② 老师卡在工具行为上（搜索词没命中 `query_match`、写不出目录）→ fixture 缺陷，同 ①；<br>③ 老师确实做错 → 移到 `bench/distill/cases-shelved/`，**不得放宽 expect 迁就老师** |

**停线规则**：一批里 0/3 的题 > 25% 时，停下来，先检查起草简报和配额再开下一批，不要靠补题凑数。
参照：DeepSeek 在 workbank 上两轮合计 94.9%，蒸馏题如果大面积 0/3，多半是题的问题。

### S6 重放切行

```bash
bin/rwkv-lab corpus render --cases bench/distill/cases --script runs/distill/$B/script.jsonl --out runs/distill/$B/corpus
```

- 不传任何额外 flag，也不用 `--` 追加 agent-eval 参数。默认值就是 workbank 的 g1k 臂，改了 wire 就和跑分对不上。
- **不得传 `--keep-failing`**（会把判分不过的轨迹放进训练集），**不得传 `--allow-test-bank`**。
- 验收：`runs/distill/$B/corpus/run/run.json` 的 `harness.wire_hash` 等于 S0 记下的值。
- `rejects.jsonl` 里每条都要有归属：`teacher trajectory fails the case expectations` 出现在 1/3 题上是正常的（S5 按老师的 run 判通过，
  S6 按当前题目重判，两者只在改过题时不同）；其他原因（生成次数不一致、非只追加、动作不同）**必须逐条查明**，那是 harness 与脚本不对齐的信号。

产物 `rows.jsonl` 每行 `{text, loss_spans, meta}`：`loss_spans` 是 Unicode 码点偏移，只覆盖老师输出；
多轮题**每轮一行**（`meta.turn`）；`meta` 带 `case_id`、`wire_hash`、`harness_version`、`canonicalized`。

### S7 批次验收

1. **行数**：至少有 1 行的题 ≥ 本批入库题数的 75%。
2. **打包检查**：`bin/rwkv-lab corpus pack --rows runs/distill/$B/corpus/rows.jsonl --exclude bench/distill/exclude.jsonl --dry-run`（§4.2）退出码 0。
3. **抽检**（主控 Agent 亲自读 `text` 中老师输出的部分）：
   - 随机 20 行（`meta.case_id` 均匀覆盖场景）；
   - **加上**所有判据为 `output_contains_any` 的题的全部行（TR-AMBIG 第 1 轮、TR-NOCAP、explain_readonly 等），这些题判分器只查关键词。
   - 查：终答是否真的对、反问是否真在问该问的东西、拒绝是否给了理由、有没有答非所问却撞上关键词。不合格的写进 `bench/distill/exclude.jsonl`，**不得手改 rows 或 script**。
4. **报告** `bench/distill/reports/$B.md`，必须包含：题数（入库 / 下架）、pass@3 分布、0/3 分诊表（ID、归类 ①②③、处置）、
   paths 丢弃原因计数、render 行数与拒绝原因、零调用行占比、抽检行数与剔除数、`wire_hash`、`bin/rwkv-cli` sha256、git commit。
5. **提交**：分支 `distill/$B`，提交 `bench/distill/cases*`、`batches.jsonl`、`exclude.jsonl`、`reports/$B.md`；不提交 `runs/`。

### S8 打包数据集

```bash
bin/rwkv-lab corpus pack \
  --rows runs/distill/b01/corpus/rows.jsonl --rows runs/distill/b02/corpus/rows.jsonl \
  --exclude bench/distill/exclude.jsonl \
  --out runs/distill/dataset-YYYYMMDD
```

- 所有 rows 必须是同一个 `wire_hash`，否则 `pack` 拒绝。harness 升级后，用当前 `bin/rwkv-cli` 对旧批次的 `script.jsonl` **重新 render** 即可。
  render 不调模型，几百条不到一秒。所以 `script.jsonl` 才是真正的资产，rows 随时可以重新生成。
- 产物：`train.jsonl`（每行只有 `{"text": …}`，当前 state 训练器只读 text）、`rows.jsonl`（完整字段，留给以后支持 `loss_spans` 的训练器）、`manifest.json`。

## 4. 前置工具改造（M0，**阻塞项**）

不做完 4.1，S2 的 lint 每题都会报 canary 违规，子 Agent 会被迫写 `WORKBANK-CANARY`，这正是要防的事。不做完 4.2，就没有可执行的数据集闸门。
两项都在 Go 侧（`internal/lab`），只用标准库和 go.mod 里已有的依赖，并带测试。

### 4.0 已修：`lint --fix` 回填 null（2026-09-25）

Go 迁移后的 `writeCaseIndented` 从顶层 `caseObj["fixture_bytes"]`（不存在）取值，导致 `--fix` 声称 `0 -> 990`，实际写入 `null`。
已改为从 `tags` 取值，回归测试 `TestLintFixBackfillsFixtureBytes`（旧代码下失败、新代码下通过）。开工前确认 main 含这个测试。

### 4.1 `bank lint --canary-prefix`

- 新 flag `--canary-prefix string`，默认 `WORKBANK-CANARY`（workbank 行为逐字节不变）。规则变为：`description` 以 `<prefix>-[0-9a-f]{8}` 结尾。违规文案里的前缀随 flag 变化。
- 加一条专门规则 `canary.foreign`：`--canary-prefix` 不是 `WORKBANK-CANARY` 时，`description`、`verify.py`、`NOTES.md` 任一处出现 `WORKBANK-CANARY` 都报错。
- 测试：
  - 正向：DISTILL 题配 `--canary-prefix DISTILL-CANARY` 时 0 违规；
  - **负向**：同一题的 description 换成 `WORKBANK-CANARY-…`、带 `--canary-prefix DISTILL-CANARY` 跑时必须报 `canary` 和 `canary.foreign`；
  - 回归：`bin/rwkv-lab bank lint`（不带 flag）对 `bench/workbank/cases` 仍是 148 题 0 违规。

### 4.2 `corpus pack`

```
rwkv-lab corpus pack --rows <rows.jsonl> [--rows …] [--exclude <jsonl>] (--out <新目录> | --dry-run) [--max-tokens 4096]
```

| 行为 | 规格 |
|---|---|
| 读入 | 多个 rows.jsonl 按参数顺序拼接；`--exclude` 里的 `case_id`（形如 `tab-5003--p1`）对应的所有行（多轮题的每一轮）剔除 |
| 闸门（任一不满足则退出码 1，不写任何文件） | ① 全部行 `meta.wire_hash` 只有一个值；② 每行 `text` 的 token 数 ≤ `--max-tokens`（用 `internal/tokenizer` 的 World 词表，与 `rwkv-lab tokcount` 同一实现）；③ 任何 `text` 中不含 `WORKBANK-CANARY` 和 `DISTILL-CANARY`（canary 只该出现在 description 和 verify.py，出现在模型可见文本里就说明 fixture 有问题）；④ 没有两行 `text` 完全相同（按 sha256） |
| 统计（stdout，`--dry-run` 也打印） | 行数；按场景（case_id 前缀）分的行数；按 `meta.turn` 分的行数；**零调用行占比**（本行 loss span 覆盖的文本里没有 `<tool_call>`）；token p50 / p99 / max；剔除行数；**按 `meta.kind`、`meta.source` 分的行数**（§4.4） |
| `--out` 产物 | `train.jsonl`（`{"text": …}`）、`rows.jsonl`（原样）、`manifest.json`：`{inputs:[{path, sha256, rows}], exclude:{path, sha256, removed}, wire_hash, harness_version, rows, tokens:{p50,p99,max}, zero_call_share, created_at}`；目录已存在则拒绝 |
| 测试 | 各闸门一条**负向**测试：两种 wire_hash 混合、超长行、含 canary 的行、重复行，每条都必须退出 1 |

零调用占比的下限（建议 ≥ 15%）先只打印不拦截，第一批跑完看实际分布再定。

### 4.3 闲聊题（`smalltalk`）的 lint 豁免

冒烟里 5 道闲聊题每题报 5 条违规，其中三条是规则本身不适用：

| 规则 | 为什么闲聊题不适用 |
|---|---|
| `answer_contract`（最后一轮必须以 `Reply with only the final answer. If you cannot determine the answer, reply exactly UNKNOWN.` 结尾） | 「Hi! Good morning. Reply with only the final answer…」会原样进训练行，教 student 在寒暄后面也期待格式指令。**闲聊题必须没有答案契约** |
| `verify`（verify.py 缺失） | 没有可独立计算的答案 |
| `trap_decoys`（single-value expectation 不许 null） | 判据是 `output_contains_any`，不是单值 |

改造：

- `bench/workbank/docs/tag-vocab.json` 的 notool 场景下加 task_type `smalltalk`（纯增量；workbank 没有这类题，lint 结果不变），`authoring-guide.md` §2 的表同步登记。
- lint 对 `task_type == "smalltalk"`：**禁止**出现答案契约（出现就报 `answer_contract.smalltalk`）；不要求 verify.py；允许 `trap_decoys` 为 null；
  **要求**每轮 `expect` 同时有 `"tools": []`、`"require_active_no_call": true` 和非空的 `output_contains_any`。
- 测试：`nt-5001..5005` 在 `--canary-prefix DISTILL-CANARY` 下 0 违规；**负向**：给 nt-5001 加上答案契约必须报错；删掉 nt-5001 的 `output_contains_any` 必须报错。

### 4.3.1 越权拒绝题（`beyond_capability` 与一切带 `TR-NOCAP` 的题）

**根因在规格，不在判据**：这类题的题面若以 `… If you cannot determine the answer, reply exactly UNKNOWN.` 收尾，等于替模型把「做不到」写成了弃权。b01 的 19 道拒绝题里老师 19/19 都答了裸 `UNKNOWN`（判据当时也认它），拿到的是「凡事答 UNKNOWN」的信号，不是拒绝。拒绝要教的是**说明做不到、为什么、能做什么替代**。

改造（只在 `ctx.distillRules` 下生效，即 `--canary-prefix` 不是 `WORKBANK-CANARY` 时——测试集是冻结的，它的拒绝题早于这条规则，不能拿新规则去报它）：

- lint 对 `task_type == beyond_capability` **或** `traps` 含 `TR-NOCAP`（不分场景）：
  - **禁止** UNKNOWN 答案契约（报 `answer_contract.refusal`）；
  - 每轮 `expect` 必须：非空 `output_contains_any` 且**词表里没有 `UNKNOWN`**、`output_excludes` 含 `UNKNOWN`、非空 `forbidden_tools`（写类工具）——缺哪条报 `expect.refusal`。
- 判据词表用拒绝语（`cannot` / `can't` / `unable` / `not able` / `do not have access` …），**去掉 `UNKNOWN`**；scorer 侧由 `output_excludes: ["UNKNOWN"]` 兜底拒绝弃权。
- **允许先查工作区再拒绝**（先确认配置，再说「我不能替你重启服务」），**不强制零调用**，因此不要 `require_active_no_call`。
- `bank verify` 对这类题的 `verify.py` 记 `verify_shape_unknown` warning（没有可独立计算的答案），与闲聊题同类，可接受。

**测试**：`cfg-5006`（b01 的旧形状）在 `--canary-prefix DISTILL-CANARY` 下必须报 `answer_contract.refusal` + `expect.refusal`；同一目录在默认前缀下**不得**报这两条。

### 4.4 训练行标签（`meta.source` / `case_tags` / `traj` / `kind`）

现状（2026-09-25 实测）：题目有标签，但训练行没有。蒸馏题的 `case.json` 有 `tags`；700 条源记录有 `scenario` 和 44 种混杂的 `behavior_tags`。
可是 `rows.jsonl` 的 `meta` 只有 `case_id`/`turn`/`passed`/`wire_hash` 这类技术字段，render 写出的中间 `case.json` 也不带 tags。
目标：**每一行自带标签**，清洗、配比、训练后分类看效果都直接 group by，不用回源关联。

**硬约束：只动 `meta`。** `text` 与 `loss_spans` 必须逐字节不变，`wire_hash` 不变。验收时对 base700 新旧两次渲染逐行比较 `text`，670 行必须全部相同。

#### 4.4.1 字段

```json
"meta": {
  "case_id": "…", "turn": 1, "passed": true, "…原有字段…": "…",
  "source": "base700",
  "seeded_from_test": true,
  "case_tags": {
    "scenario": "filesystem",
    "task_type": "find_file",
    "traps": [],
    "level": null,
    "family": "grp-fs-0001-b1",
    "behaviors": ["multi_hop", "answer_exact_text"],
    "origin": {"parent_seed_id": "fs-0001", "branch": "b1", "split": "train",
               "behavior_tags": ["lookup_value", "exact_text", "multi_hop", "no_tool_closeout"]}
  },
  "traj": {
    "turns_total": 1,
    "tool_calls": 3,
    "tool_seq": ["list_files", "read_file", "read_file"],
    "zero_call": false,
    "web": false,
    "local": true,
    "writes": false,
    "unsupervised_outputs": 0,
    "final_kind": "value",
    "tokens": 2310
  },
  "kind": "local"
}
```

| 字段 | 来源与规则 |
|---|---|
| `source` | render 新增**必填** flag `--source <名字>`（`base700`、`distill-b01`…）；不给就报错退出，**不设默认值**（有默认值就会出现一批标错来源的数据） |
| `seeded_from_test` | records 模式：`parent_seed_id` 在 `bench/workbank/cases` 或 `cases-shelved` 里存在就是 true（base700 应当 670/670 为 true）；cases 模式：一律 false |
| `case_tags` | cases 模式：原样取自 `case.json` 的 `tags`，只保留 `scenario task_type traps level family`，另加 `behaviors: []`；records 模式：按 4.4.3 规范化 |
| `traj` | 由 `corpus rows` 从**本行**（本轮）的脚本输出计算：`tool_calls`、`tool_seq` 只统计本轮的 `supervised` 输出；`unsupervised_outputs` 统计本轮 `supervised:false` 的输出（base700 的 119 条恢复前缀在这里为正数）；`tokens` 用 World 词表数 `text` 的 token |
| `traj.web` / `local` / `writes` | `web` = 用过 `web_search` 或 `web_fetch`；`writes` = 用过 `write_file`、`replace_lines` 或 `append_file`；`local` = 用过除 web 类、写类、`calculator`、`datetime` 之外的任何工具 |
| `traj.final_kind` | 本轮最后一次输出 `strip()` 后：等于 `UNKNOWN` → `unknown`；等于 `DONE` → `done`；本轮 `expect` 有 `expected_number` 或 `output_equals` → `value`；其余 → `text`。本轮最后一次输出是工具调用时（多轮题的中间轮）→ `none` |
| `kind` | 按 4.4.2 推导 |

#### 4.4.2 `kind` 推导（自上而下，取第一个命中的）

| # | 条件 | `kind` |
|---|---|---|
| 1 | `task_type == "smalltalk"` | `smalltalk` |
| 2 | `zero_call` 且（`task_type == "beyond_capability"` 或 `traps` 含 `TR-NOCAP`） | `refuse` |
| 3 | `traps` 含 `TR-AMBIG` 且 `turn < turns_total` | `clarify` |
| 4 | `zero_call` | `direct` |
| 5 | `scenario == "script"` 或 case 有 `expect.run` | `script` |
| 6 | `writes` | `write` |
| 7 | `web` 且 `local` | `web_local` |
| 8 | `web` | `web` |
| 9 | 其余（含只用 `calculator`/`datetime`） | `local` |

同一题的不同轮可能属于不同 kind（歧义题第 1 轮是 `clarify`，第 2 轮是 `local`），这是预期结果。
规则 3 **不看 `zero_call`**：先翻工作区、发现两个候选再问「你指哪个」比不看就问更有依据；「有没有调用工具」已经记在 `traj.zero_call` 里，需要时与 `kind` 组合筛选即可。
`corpus pack` 的统计增加一张「kind × 行数」表，`--dry-run` 也打印。

#### 4.4.3 base700 标签规范化（产出 `bench/distill/tag-map.json`，入库）

规范化规则写成数据文件，render 在 records 模式下读它，**不写死在 Go 里**：映射有人工判断的成分，要能审阅、能改。结构：

```json
{
  "task_type_overrides": {"ws7-fs-0001-b10": {"task_type": "find_file", "reason": "…"}},
  "behaviors": {"multi_hop": "multi_hop", "source_pair": "multi_source", "pure_value": null},
  "undefined": ["no_tool_closeout"]
}
```

**task_type**：取 `behavior_tags` 中属于该 scenario 合法值（`tag-vocab.json` 的 `task_types[scenario]`）的那一个。实测结果：

| 情况 | 条数 | 处理 |
|---|---|---|
| 恰好 1 个合法值 | 661 | 直接用 |
| 2 个合法值（`ws7-log-0003-x10`：`count_events`+`time_window`） | 1 | 取 `time_window`（区分性更强的那个），写进 overrides |
| 0 个合法值：用了别的场景的 task_type | 38 | 执行者**逐条读题面**，从本场景合法值里选一个，写进 overrides 并附理由。下表是建议，读完题面可以改 |

| scenario | 原标签 | 条数 | 建议映射 |
|---|---|---|---|
| code | `lookup_value` | 1 | `locate_definition` |
| docs | `filter_count` | 2 | `extract_items` |
| docs | `merge` | 4 | `write_structured`（都带 `artifact_file`） |
| filesystem | `lookup_value` | 7 | `find_file` |
| filesystem | `aggregate` | 10 | `count_by_type` 或 `largest`，看题面 |
| filesystem | `filter_count` | 6 | `count_by_type` |
| filesystem | `lookup_value`+`aggregate` | 4 | `count_by_type` |
| hybrid | `write_structured` | 1 | `web_then_edit` |
| logs | `filter_count` | 3 | `count_events` |

**behaviors**：44 个原标签里，task_type 以外的 17 个按下表处理。原值一律保留在 `origin.behavior_tags` 里，不丢。

| 原标签 | 条数 | 规范后 | 理由 |
|---|---|---|---|
| `multi_hop` | 275 | `multi_hop` | |
| `source_pair` | 116 | `multi_source` | 与 authoring-guide 的 TR-MULTISRC 同义 |
| `count_discipline` | 213 | `count_discipline` | |
| `precedence_rule` | 125 | `rule_precedence` | 与 task_type `precedence` 区分 |
| `abstain_unknown` | 51 | `abstain_unknown` | |
| `stop_when_insufficient` | 52 | `stop_insufficient` | |
| `empty_result_interpreted`、`source_empty` | 52+1 | `empty_result` | 同一件事 |
| `exact_text` | 118 | `answer_exact_text` | |
| `json_answer` | 1 | `answer_json` | |
| `pure_value` | 406 | 丢弃（`null`） | 默认答案形态，没有区分度 |
| `source_local`、`source_web` | 366、68 | 丢弃 | 由 `traj.local` / `traj.web` 从实际轨迹计算，更可信 |
| `artifact_file` | 141 | 丢弃 | 由 `traj.writes` 计算 |
| `script_run` | 80 | 丢弃 | 由 `kind == script` 体现 |
| `recovery_after_error` | 123 | 丢弃 | 由 `traj.unsupervised_outputs > 0` 体现 |
| `no_tool_closeout` | 332 | 列入 `undefined`，只留在 origin | 700 条的文档里找不到定义，不猜它的语义 |

`family` 取记录的 `instance_group_id`；`traps` 为 `[]`、`level` 为 `null`（700 条没有标这两项，**不要事后补猜**）。

#### 4.4.4 验收

- base700 重新渲染（`--source base700`）：670 行 `text`、`loss_spans` 与旧渲染逐行相同；`seeded_from_test` 670/670 为 true；
  每行 `case_tags.task_type` 都在该 scenario 的合法值里；`tag-map.json` 的 overrides 恰好覆盖 39 条。
- 5 道闲聊题（`--source distill-smoke`）：`kind` 全部为 `smalltalk`，`traj.zero_call` 为 true，`final_kind` 为 `text`。
- 单测：9 条 `kind` 规则各一条用例；`final_kind` 五种取值各一条；**负向**：不给 `--source` 必须退出 1；
  records 模式下有记录的 task_type 无法解析、tag-map 里也没有 override 时必须退出 1，不能静默写空值。
- `rows.jsonl` 新增字段后，`corpus pack` 产出的 `train.jsonl` 仍然只有 `{"text"}`（训练器不受影响）。

## 5. 执行者容易悄悄搞砸的地方

| 做法 | 后果 |
|---|---|
| 让子 Agent「参考一下 workbank 的题」 | 泄漏。跑分虚高，而且 decontam 查不出来 |
| 为了让老师通过而放宽 `expect`（加容差、改 `output_contains_any`、删 `forbidden_tools`） | 判分器是数据质检员，放宽就是往训练集里放错轨迹 |
| 按老师的答案改 verify.py / expected | 同上。老师与 verify.py 不一致时，**以 verify.py 的独立计算为准**去查题 |
| 手改 `script.jsonl` 或 `rows.jsonl`（删一步、改 supervised、修个答案） | 行与 harness 不再逐字节对齐；而且全文 loss 训练器会把改坏的地方学进去。剔除只走 `exclude.jsonl` |
| `--max-per-case` 调大 | 简单题一题出 3、4 条相似轨迹，数据分布向简单题倾斜 |
| 把零调用行当成「空行」过滤掉 | 训练出只会调工具的模型（state LR 扫描的 bfcl 崩溃就是这么来的） |
| render 时追加 agent-eval flag，或中途重编 `bin/rwkv-cli` | `wire_hash` 分裂，训练 wire 与跑分 wire 对不上 |
| 老师用 T=0「为了稳定」 | DeepSeek-flash 在 T=0 下崩溃 |
| decontam 命中后调阈值 | 闸门失效 |
| 用 `WORKBANK-CANARY` 让 lint 通过 | 见 §2.2 |
| 提交 `runs/` 下的东西 | 仓库约定：派生数据不入库 |
| 在 0/3 题上多跑几次直到蒙中 1/3 | 等于在不可靠的题上抽奖；0/3 先分诊，分诊结论是「老师确实不会」就下架 |

## 6. 这不是 bug

- `corpus paths` 丢掉大量路径（`duplicate path`、`same tool sequence`）：设计如此，同一题不要多条相同轨迹。
- 老师的参数带奇怪的习惯值，例如 `list_files` 的 `{"max_depth":8,"max_results":500}`：`paths` 只去掉等于默认值的参数，其他照原样保留，这就是老师的真实动作。
- `meta.canonicalized > 0`：Go 把 tool call JSON 里的 `<` `>` `&` 转义成 `<` 等，训练行采用 harness 的字节。这是 student 在历史里实际看到的。
- 多轮题一题出多行，前几轮以提交后的历史出现，只有本轮输出有 loss span。第 2 轮的历史里没有第 1 轮的 post-tool 提醒，跑分时也是这样。
- `bank verify` 对写文件类题报 sabotage `warning`（跳过）：可接受；只有 `sabotage_undetected` 是失败。
- `bank verify` 的破坏测试删掉了 CSV 表头，导致 verify.py 崩溃、判为「已检出」：这是破坏测试的兜底方式，可接受。
- lint 要求 `llm:` 作者配 `status: draft`：蒸馏题本来就永远是 draft。
- 零调用题每题最多只有 1 条路径（`paths` 报 `dropped: same tool sequence`）：k 次的工具序列都是空的，选路按工具序列去重。终答措辞不同也只留最短的一条。要措辞多样性就多出题，不要改 `paths`。
- 训练行比旧的 700 条平均长约 250 token：多出来的是 harness 的 post-tool 提醒，这正是改用重放的原因。

## 7. 里程碑

| 里程碑 | 内容 | 验收 |
|---|---|---|
| **M0（阻塞，约 1 天）** | §4.1、§4.2、§4.3、§4.4 | `go test ./internal/lab/...` 全过，§4 列出的负向测试齐全；§4.4.4 全部满足；`bin/rwkv-lab bank lint` 对 workbank 仍 0 违规；把 §2.5 样例放进 `bench/distill/cases/tabular/tab-5001/` 后，`lint --canary-prefix DISTILL-CANARY` 0 违规 |
| **M1 冒烟（10 题）** | 每场景 1 题（含 tab-5001）走 S1–S7 全流程 | 老师 k=3 至少 8 题 ≥ 1/3；render 的 `wire_hash` = S0 值；`pack --dry-run` 退出 0；**负向**：手工把一题 `expected_number` 改错后重跑 S6，该题所有行必须进 `rejects.jsonl` |
| **M2 b01（200 题）** | §2.4 配额，S1–S7 | S7 全部条目；报告入库 |
| **M3 数据集 v1** | S8 打包 b01 | `manifest.json` 齐全；交给用户训练 state，并在 workbank 上与不训练的基线对比（按 rwkv-bench skill 的规程，不属于本流程） |
| M4+ | b02 起每批 400 题；配额按 b01 报告和 M3 的训练结果调整 | 同 M2 |

## 8. 待用户填写 / 决定

| 项 | 需要的内容 |
|---|---|
| 老师端点 | `$TEACHER_URL`、`$TEACHER_MODEL`、key 所在的环境变量名；官方还是中转 |
| 起草模型 | 子 Agent 用什么模型（写进 `tags.author` 与 `batches.jsonl`） |
| 目标规模 | 数据集 v1 要多少行；决定 M4 之后跑几批 |
| `script.jsonl` 入库 | 建议入库到 `bench/distill/scripts/<batch>.jsonl`：老师轨迹是花钱买的，采样也不可复现，而 rows 能由它在任何 harness 版本下重新生成。这与「派生数据不入库」的约定冲突，需要你拍板 |
| 零调用占比下限 | §4.2 先只打印；b01 之后定数 |
| 回答风格 | Qwen 的直答是重 Markdown 加 emoji（「**📁 Work with files…**」、多级列表），student 会原样学去。可选做法：接受；或者在抽检时剔除；或者给 agent-eval 加一个只对老师生效的风格提示（老师的 wire 不进数据，所以不影响训练行字节，但要改代码）。需要你定 |
