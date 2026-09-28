# workbank 判分口径审计（2026-09-21）

审计对象：`deepseek-flash-nexttoken`，k0–k3 × 40 题，harness v21，`--max-steps 10`，`case_parallelism 4`（k0 为 40）。
运行目录 `runs/workbank/flash-nexttoken-k{0..3}-20260921`。同名 `-INVALID-upstream503` 目录是 15:29 那批 503 中断的作废跑，未入账，不在本审计内。

官方成绩 **129/160 = 80.6%**（k0 30 / k1 32 / k2 35 / k3 32）。
本审计的结论是：**31 次失分里只有 5 次是真实能力问题**，26 次来自判分器、harness 或题目设计。

## 1. 失败归因

逐 case-run 读 `summary.json` 的 failure 字符串与模型原始输出分类，四轮共 31 次失分：

| 类别 | 次数 | 题 |
|---|---:|---|
| 判分器假阴性 — 数字带单位 | 5 | nt-0001 ×4、hyb-0002 k3 |
| 判分器假阴性 — 大小写/尾部句读 | 3 | cfg-0003 k0/k1、doc-0002 k1 |
| 判分器假阴性 — 自然语言答案用 `output_equals` | 1 | web-0002 k1 |
| 设计缺陷 — 零调用与答案耦合 | 8 | nt-0002 ×3、nt-0003 ×4、nt-0004 k1 |
| harness — 上游 continuation 中断 | 3 | cfg-0001 k0、cfg-0003 k3、scr-0003 k3 |
| harness — answer contract `role_header` | 3 | cfg-0004 k0、scr-0003 k0、scr-0004 k3 |
| 题目歧义 | 3 | hyb-0004 ×3（答 14588.34） |
| **真实能力失分** | **5** | hyb-0002 k0/k2 弃权、cfg-0003 k2 答 Yes、scr-0004 k0/k2 撞步数上限 |

### 1.1 数字带单位（5 次）

`parseNumericOutput` 原本只接受符号 + 单个货币符 + 千分位逗号。

| 题 | 模型输出 | 期望 | 结果 |
|---|---|---|---|
| nt-0001 ×4 | `9000 MiB per hour` | 9000.0 | 数值精确命中，判挂 |
| hyb-0002 k3 | `9806.55 EUR` | 9806.55 | 数值精确命中，判挂 |

全库 17 道 `expected_number` 题中，只有这 2 道的 prompt 主动指定单位（"express that same rate in MiB per hour"、"their total value in euros"），命中率 2/2。changelog 2026-09-17 已把 tab-0004 的 `$23,609.60` 同类假阴性记为「留待校准环节从判分侧处理」。

### 1.2 大小写与尾部句读（3 次）

`answerFailures` 原本只 `TrimSpace`。cfg-0003 答 `No`（期望 `no`）两次；doc-0002 答 `45 days.`（期望 `45 days`）一次。全库 11 道 `output_equals` 题里 5 道是裸数字、1 道是 yes/no，暴露面相同。

### 1.3 自然语言答案用 `output_equals`（1 次）

web-0002 k1 答 `45 seconds (deltastream 3.0.0 default; it was 120 seconds before 3.0.0)`：答案正确、正确避开了题目埋的过时博客、并给了出处，因不等于 `45` 判挂。

### 1.4 零调用与答案耦合（8 次）

`expect.tools: []` 原本直接产生 turn 失败。这 8 次的答案全部正确：nt-0002 三次答 `443`，nt-0003 四次、nt-0004 一次答 `UNKNOWN`——而 nt-0003 的 `output_contains_any` 明确把 `UNKNOWN` 列为接受值。

nt-0003 尤其反向：题目要求「把 CSV 邮件给 Ada」，模型先查工作区确认有无该能力再拒绝，比闭眼拒绝得分更低。nt-0004 的 `["720","UNKNOWN"]` 判据进一步使「算出数字」与「直接弃权」同分。

### 1.5 harness 故障（6 次）

- `Chat Completions continuation error: function tool call N arguments are not a JSON object` ×3：`ErrRemote`（上游/传输层），turn 直接中断、输出为空。原本记 0 分。
- `answer contract repaired: [role_header]` ×3：回复以 `Assistant:` 开头 → 整段被替换为兜底句并判失败。但 scr-0004 k3 的原始输出显示 report.py 已正确重建，cfg-0004 k0 的原始输出就是 `Assistant: DONE`。

  **归因更正（2026-09-21 第二轮）**：本节初稿把这 3 次记为「线格式脏 / 模型违反了只回答最终答案的契约」，**这个定性是错的**。原生 chat 路径下 `withAssistantPrefix`（`chatcompletions/config.go`）并不做真 prefill，而是往 system 里塞一条指令：「回答必须恰好以 `"Assistant:"` 开头，前面不得有任何文本」。模型照做，`validateAnswer` 随即判 `role_header` 违规。**harness 命令模型输出的东西，正是 harness 自己的校验器禁止的东西**，模型全程在服从指令。根因在 `native_tools.go`：提供工具时会清掉该前缀，唯独答案阶段（`tool_choice=none`）漏了。已由 `nativeAssistantPrefix()` 在源头拒绝下发，实测该前缀出现 3 次 → 0 次。把 `role_header` 从 pass/fail 降级为指标仍然正确，但那只是缓解，真正的修复是不发这个前缀。

### 1.6 题目歧义 — hyb-0004（3 次）

模型 3/4 轮稳定答 `€14,588.34`（6 月牌价），期望 14746.84（9 月牌价）。发票全为 8 月，9 月牌价 effective 8 September、8 月不适用；题面问 "prevailing desk rates"，按当期有效牌价折算 8 月应收款是会计常规。题目把这个读法标为 TR-SUPERSEDE decoy，违反出题手册 §1.4「答案唯一」。

  **归因更正（2026-09-21 第二轮）**：题面歧义只是次要成因，**主因是 harness bug——这道题自出题起就无解**。`webfixture.go` 的 `Fetch` 用 `strings.Contains` 取**第一个**匹配，而六月牌价的 `url_match`（`www.aldermoor.example/fx/desk-rates`）是九月牌价 URL（`.../desk-rates-september`）的前缀且声明在前，于是无论请求哪个 URL 都返回六月表内容。**模型每次答 14588.34 都是如实报告它唯一能看到的汇率。**改为取最长匹配后，模型立刻算出 14746.84。本节原先「所有模型所有配置下都是 0 分」的观察，正确解释是这个，不是题难。

### 1.7 scr-0004 的锚点硬币

`expect.run` 原沙箱布局：

```
sandbox/                                  ← cwd
├── hidden/transactions-2026-09-eu.csv    ← 隐藏输入，在 workspace 之外
└── workspace/report.py                   ← 脚本在这里
```

README 写「scheduler 以项目根为工作目录启动」「sweep the entire project tree」。实测两种都忠实于题面的写法：

```
os.getcwd()                                → total,1503785  通过
os.path.dirname(os.path.abspath(__file__)) → total,1397935  挂（MER-3106 整个消失，差 105,850）
```

k1 通过那轮写的正是 `os.getcwd()`。而 **scr-0001/0002/0003 的 fixture 脚本全部用 `Path(__file__).resolve().parent`** ——题库自己教的写法，正是 scr-0004 判挂的写法。

## 2. 顺带查出的两处基础设施缺陷

**2.1 `run.json` 丢失零调用契约。** `Expectation.Tools` 标签为 `json:"tools,omitempty"`，空切片被丢弃：

```
case.json : {"expected_number": 9000.0, "tolerance": 0.01, "tools": []}
run.json  : {"expected_number": 9000,   "tolerance": 0.01}
```

「无约束」(nil) 与「要求零调用」(empty) 往返后不可区分。线上判分不受影响（跑分时 case 从题库目录加载），但一切基于冻结清单的离线复盘都看不见 notool 契约——这正是 `scorer_ablation.py` 只捞回 nt-0001/web-0002、捞不到那 8 次的原因。

**2.2 NOTES 与 case.json 漂移无闸门。** nt-0001 v2 改题后 NOTES 整段停留在 v1：参考答案仍写 9437.184，并把 v2 的**正确答案 9000** 列为「failing traces 里应当看到的 careless value」；description 也仍写 "MB per hour"。本轮该题 4/4 挂在 9000 上，照此文档复盘必然得出「模型混淆 MiB/MB」的错误结论。nt-0003/0004 的 Traps 段同样称 UNKNOWN 是 decoy，与 expect 块矛盾。新增的 `notes.answer` 闸门上线后立即又查出 fs-0001（NOTES 指名了最大文件却从未写出 497，且「outweighs by several hundred bytes」与实际 156 字节不符）。

## 3. 诊断口径重打分

`tools/scorer_ablation.py` 能逐字节重建官方成绩（30/32/35/32），确认归因读法可靠。累积放宽各缺陷类后：

| arm | k0 | k1 | k2 | k3 | total | pass% |
|---|---:|---:|---:|---:|---:|---:|
| official | 30 | 32 | 35 | 32 | 129/160 | 80.6% |
| A +大小写/句点归一 | 31 | 34 | 35 | 32 | 132/160 | 82.5% |
| B +接受带单位数字 | 32 | 35 | 35 | 34 | 136/160 | 85.0% |
| C +零调用解耦 | 32 | 35 | 35 | 34 | 136/160 | 85.0% |
| D +作废 harness 故障 | 34 | 35 | 35 | 34 | 138/157 | 87.9% |

C 臂在该脚本里零收益，原因即 §2.1：冻结清单读不到 `tools: []`，无从松弛。按 `summary.json` 的实际 failure 字符串手工核算，这 8 次应全部转为通过，C 臂真实值约 **144/160 (90.0%)**，D 臂约 **146/157 (93.0%)**。

**这些是诊断数字，不是官方成绩。** 本轮未回填重打分任何历史 run。判分口径与两道题面同时变更，2026-09-21 及之前的分数须在新口径下重跑才能与之后比较。

## 4. 已落地的修改

判分（scorer v3）、harness（上游作废 / `expect.run` 布局 / `Tools` 序列化）、两道题面返修（hyb-0004 v3、scr-0004 v2）、四处文档同步、两条新 lint 闸门与配套回归测试，逐项见 `docs/changelog.md` 的 2026-09-21 条目；出题侧规矩见 `docs/authoring-guide.md` 反例 X-004..X-007。

闸门状态：lint 40/40 零违规；verify_all 40/40；`go test ./...` 全绿（`runs/budget-language-audit-20260920/build-overlay` 的构建失败早于本次改动）。
bank_version `sha256:324d0ea9…e1f66` → `sha256:1b8cbe75011dfe662357666797962b86bd55a3a9957f0d99244f182f0675846d`。

## 5. 复现

```sh
# 归因（读 summary.json 的 failure 字符串）
python3 bench/workbank/tools/scorer_ablation.py \
  runs/workbank/flash-nexttoken-k{0,1,2,3}-20260921 --out /tmp/ablation.json

# 闸门
python3 bench/workbank/tools/lint.py
python3 bench/workbank/tools/verify_all.py --cases bench/workbank/cases
python3 bench/workbank/tools/test_lint.py
go test ./internal/agent/eval/
```

---

# 第二轮：参考天花板可解性与模型梯队（同日）

目标经用户改定：**不追求区分度，改为证明参考天花板可达**——40 题须在强模型上稳定全过，以此证明题目有解；弱模型不要求全过。纪律：只修有正当缺陷的题（歧义、不公平格式要求、harness 伪影），模型确实做错的不动，否则是把题库过拟合到 DeepSeek。

## 6. 第二轮修掉的缺陷

| 对象 | 缺陷 | 判定 |
|---|---|---|
| `webfixture.go` | `Fetch` 取第一个子串匹配，六月 `url_match` 是九月 URL 的前缀 → **hyb-0004 自出题起无解** | harness bug |
| hyb-0004 v3→v5 | 拿 9 月牌价重估 8 月应收款反直觉；v3/v4 两次改仍不过（模型取齐证据后反复 web_search 烧光 16 步） | 题面缺陷，改为当天结汇 |
| cfg-0003 v2→v3 | 题面以 "Quick check" 开头诱导跳过 merge 规则，考的变成「抵抗快字暗示」 | 题面缺陷，1/3 → 3/3 |
| code-0003 v2→v3 | `auth/bootstrap.py` 顶层调用无 import，真跑 NameError，「算不算调用点」未交代；**贪心下 3/3 稳定失败** | fixture 缺陷 |
| `native_tools.go` | 答案阶段仍下发 `assistant_prefix`，模型照做后被自家 `validateAnswer` 判违规 | harness 自伤（见 §1.5 更正） |
| `client_sdk.go` | 多余 tool call 的 decode 先于截断；文本线拒绝 >4 停止序列 | harness bug |
| `main.go` | `--temperature 0` 被拒，贪心解码不可用 | 工具限制 |

**code-0003 的连带发现**：补 import 后 sabotage 探针报 `sabotage_undetected`——第一行只有 import 时，删掉它三个调用点仍在，该行对答案无约束力。改为 import 与调用同行：既是合法 Python，又让被删的行真正承载答案。这说明 `verify_all` 的 sabotage 探针是有效的，它抓住了一个人工复核会漏掉的问题。

## 7. 模型梯队

`--max-steps 16 --decision-max-tokens 8192 --max-tokens 4096 --temperature 0`（DeepSeek 为 temp 0.01/并发 12，余额耗尽前的最后一组干净数据；Qwen 为本地 vLLM/并发 40）。

| 配置 | 分数 | protocol | closeout | 能力读数 |
|---|---|---|---|---|
| DeepSeek flash（参考天花板） | 115/118 = 97.5% | 0.0% | 0.0% | 是 |
| Qwen3.8-27B 思考关 | 108/118 = 91.5% | 0.0% | 0.0% | 是 |
| Qwen3.8-27B 思考开 | 103/119 = 86.6% | 0.8% | 0.0% | 是 |
| Qwen3.5-9B 思考关 | 81/120 = 67.5% | 0.0% | 0.0% | 是 |
| Qwen3.5-9B 思考开 | 80/120 = 66.7% | 0.0% | 0.0% | 是 |
| G1K RWKV（历史 closeout v0–v3） | 12/160 = 7.5% | **55.6%** | 8.8% | **否** |

三档（97.5% / 91.5% / 67%）单调分开且 protocol/closeout 全 0：题目有区分度，区分的是能力而非协议流畅度。

**思考开关两模型都是关的略好。** 27B 差 5 个百分点，且思考开时 format 层失分 1→6——思考模式让它更爱写解释，更易违反「只回答最终答案」。对 workbank 这类任务，决定成败的是工具纪律与证据处理，不是推理深度；这对 RWKV 的训练方向有直接参考（不必先追思考能力）。

**RWKV 与 Qwen 是两种病。** RWKV 89 次协议层失败（55.6%），27B 仅 1 次、9B 零次。那个 7.5% 不是「做不对题」而是「发不出合法交互」。**RWKV 的第一关是把 protocol 压到 0**，之后 capability 层的分数才开始有意义。

## 8. 陷阱有效性（首次测量）

`trap_decoys` 此前只被 lint 校验标签，从未与模型输出比对。跨全部配置汇总：

```
有效:  TR-RULEFILE 36.8%  TR-FETCHFAIL 21.1%  TR-PRECEDENCE 21.1%
       TR-CLAIM 15.8%  TR-DATEFMT 15.8%  TR-DECOY 13.2%
       TR-DUPROW 10.5%  TR-MULTISRC 10.5%  TR-WEBSTALE 10.5%  TR-SUPERSEDE 1.8%
零命中: TR-ABSENT  TR-DIRMAP  TR-NEARNAME  TR-NOCAP
        TR-NOTOOLNEED  TR-NUMFMT  TR-SIGN  TR-SNIPPETVAGUE
```

DeepSeek 单独跑时 18 个陷阱里 16 个看着像死的；9B 一测就踩（TR-CLAIM 50%、TR-DECOY 22.2%、TR-DATEFMT 33.3%），**证实陷阱是活的，只是需要够弱的模型才测得出来**。

口径限制：decoy 匹配是字符串/数值比对，语义型（TR-NOCAP 的假成功声明、TR-SNIPPETVAGUE）可能漏判；数字型（TR-NUMFMT、TR-SIGN、TR-DIRMAP）的零命中较可疑。**用户判定：陷阱是否被踩不是必选项，题目可解且无缺陷即可**，故本轮未因零命中改动任何题。

## 9. 复现

```sh
# 分层归因 + decoy 命中率
python3 bench/workbank/tools/capability_gate.py runs/workbank/<run dirs> --label NAME

# 闸门
python3 bench/workbank/tools/lint.py
python3 bench/workbank/tools/verify_all.py --cases bench/workbank/cases
python3 bench/workbank/tools/test_lint.py
go test -tags chatcompletions ./internal/... ./cmd/...
```

bank_version `sha256:aeed5395b5ed3c8a0ab5926fc6f5ab227fc0d17c03a06b135fae927f5f605ccf`（40 题 reviewed）。
本轮各批跑分均未入账 ledger：判分口径连变两次、题面改了四道，新旧行不可直接比。
