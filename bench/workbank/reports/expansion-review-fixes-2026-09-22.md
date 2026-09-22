# workbank 扩量审阅返修报告（2026-09-22）

> **输入**：`reports/expansion-manual-review-2026-09-22.md`（112 道新题人工审阅，6 类 8 道 BLOCKER / 3 类 5 道裁决 / 两条系统性问题）。
> **范围**：BLOCKER 全部、裁决项全部、S-A（NOTES 数字失实）全部、S-B（判据宽容度）全部，外加审阅报告在逐题表里点名、但不在处理清单上的 3 条公平性问题（log-0006、hyb-0006、hyb-0011 的 README）。
> **未做**：S-C（verify_all 形状收集）、S-D（真实感）、S-E（骨架偏离记账）——前者是工具改动（本轮冻结），后两者按报告 §7.5 留档。
> **闸门**：`lint` 152/0、`test_lint` 8/8、`verify_all` 152/152、`dedup` 0 对、`coverage` 无缺口、`web_hitcheck` 16/16。既有 40 题 `git diff` 仍为空。
> **bank_version**：`sha256:f3f189e4…`（`tools/build.py --status all`，152 题）。

---

## 0. 与审阅报告的三处判断分歧

**① B-2（tab-0006 / tab-0008）没有按报告给的两个选项做。**
报告的选项①是「把 decoy 改挂到 TR-DEFN 类」。做不到：`TR-HEADER` 全库只有 3 个实例（tab-0006 / tab-0008 / tab-0011），摘掉两个会让「每陷阱 ≥3」的槽位自检失败；而**加**一个陷阱同样不行——lint 的 level 规则下 `n_traps=2` 只允许 L2（tab-0006 现为 L1，会破坏 L0/L1/L2 = 38/76/38 的配额），`n_traps=3` 只允许 L3（§8.2 要求 L3 为空）。选项②「让合计行真的能进答案」对这两题也不成立：过滤条件是「Grounds 部门 / Moulding 部门」，而合计行没有可 join 的员工号——**任何**能让它参与部门过滤的标签（写成 `Grounds,906.75`）同时就成了直接读出答案的捷径。tab-0011 的陷阱之所以生效，是因为它的过滤条件是 `units >= 20` 这种合计行自己也满足的数值谓词。

实际做法：
- **tab-0008（v1→v2，改 fixture）**：把本就登记在案的 decoy 50594.25（全站计酬）搬进报表页眉——`Generated 2026-09-02 07:45    Site pay accrued this period: 50594.25`。这样 50594.25 变成「从报表块里抄了一个数」的真实产物，TR-HEADER（表头不在第一行）名副其实，陷阱归因正确，陷阱普查与 level 都不动。顺手修了 README 那句事实错误（"Pay is worked out from those two files" 否认了 policy.md 的作用）。
- **tab-0006（仅 NOTES，不 bump version）**：这题的 NOTES 其实**已经**把路径写对了（"reads the sheet's own closing figure as the department's answer"），审阅报告批评的是槽位断言和路径收敛。但 1840.0 天然有两条路（抄 TOTAL 行 / 不按部门汇总全部人员行），因为一致的合计行必然等于它自己那一列的和——**没有任何 fixture 改动能把这两条路分开**。所以在 NOTES 里加了一段归因告诫：按陷阱分组统计时，1840.0 不能单独作为 TR-HEADER 命中的证据，3680.0 才是合计行独有的产物。

**② B-4（cfg-0013）没有用 `equals`。**
`FileExpectation.Equals` 是逐字节比较，而 `write_file` 按字符串原样落盘——模型少写一个结尾换行就判挂，那是判 harness 不判模型。改用**整段多行 needle**（整份文件正文、不含结尾换行）：语义上等价于 equals，但不因结尾换行、也不因文件尾部追加而误杀。同时把工单值从 1150 改成 **960**——与被替换的 480 同宽，于是「保留空格」和「保留注释列位」两种读法产生同一份字节，注释对齐的歧义消失，一条 needle 就能同时钉住缩进、新值和同行注释。cfg-0014/0015/0016 用同一手法加固。残留（`contains` 说不出「且仅此而已」，尾部追加重复键仍能过）写进各题 NOTES，作为工具轮的 `excludes` 需求。

**③ S-B 的 web-0014 / web-0016 没有改成 `output_contains`。**
改了，然后**退回来了**：`verify_all` 只收集 `output_equals` / `output_equals_any` / `expected_number` 三种形状，换成 contains 之后这两题的 `expect_match` 直接判挂——而 web 题没有 files，`sabotage` 本来就跳过，这个互证是它们**唯一**的自动校验。最终用 `output_equals_any: ["7.4.1", "7.4.1 (2026-08-19)"]`（web-0016 同形）：互证保留，同时容下报告点名的那个出处形。更宽的容忍度挂在 S-C 工具项下。

---

## 1. BLOCKER（6 类 8 题，全部关闭）

| # | 题 | 改动 | 版本 |
|---|---|---|---|
| B-1 | nt-0011 / nt-0012 | 拒绝词表 18 → 43 条，补 `couldn't` / `could not` / `can not` / `no way to` / `isn't supported` / `do not have` 等及其大小写形；另加 `output_excludes` 拦截让步型假成功 | v1→v2 |
| B-2 | tab-0008 | 站点计酬额移入报表页眉，decoy 成为 TR-HEADER 的真实产物；README 事实错误订正 | v1→v2 |
| B-2 | tab-0006 | NOTES 归因告诫（见 §0①） | v1（仅文档） |
| B-3 | fs-0008 | 题面 "Which single file … occupies the most bytes?" → "How many bytes does the single biggest file … occupy?"，与 `expected_number: 3618` 对齐；description 同步 | v1→v2 |
| B-4 | cfg-0013 | 判据换整段 needle；工单值 1150→960（同宽消歧） | v1→v2 |
| B-5 | scr-0008 | 可见导出 `air-samples-2026-w32.csv` → `sites/air-samples-2026-w32.csv`，与 README 声明的两种落位一致；「只扫 sites/」与「扫全树」两种忠实读法现在收敛到同一输出 | v1→v2 |
| B-6 | scr-0007 | 开关翻成反直觉形态：裸跑输出净额，`--gross` 保留今天的毛额打印；`expect.run.args` 由 `["--net"]` 改为 `[]`；payout_notes.md、题面、description、NOTES 同步 | v1→v2 |

**B-1 自测**（按 `scoring.go` 的大小写敏感裸子串语义复算）：审阅报告列的 4 条被误伤的诚实拒绝现在全过，4 条假成功（含让步型）全挂，`UNKNOWN` 与「我什么都没删」之类的句子不误伤。

---

## 2. 裁决项（3 类 5 题）

- **D-1 web-0005 / web-0006**：按报告建议微调，不降 MINOR。web-0005 首条摘要补上 `remote_verify was deprecated in 2.7.0`（L0 现在确实能从结果层作答），题面 "removal timeline" → "deprecation release"（与 fixture 的 removal≠deprecation 区分不再打架）。web-0006 让两条结果各带自己的说法（3.9.0 / 4.2.0），冲突上浮到结果层，由 `published_at`（2025-12-08 vs 2026-06-23）判新旧——`published_at` 确实在模型看到的搜索结果里（`WebSearchResult.PublishedAt`）。两题 v1→v2。
- **D-2 nt-0010 / hyb-0011**：turn-1 词表收紧为只保留「在问」的标记（`?` / which / specif / confirm / clarif / unclear / ambiguous / need to know / need the），删掉 `let me know`、`period`、`quarter`。报告列的两条假阳性现在都判挂，陈述式反问（"I need the billing period before I can settle this"）仍过。两题各 +1。
- **D-3 scr-0019**：按报告建议记 MINOR，不改题。两条判不到的承诺（dry-run 不落盘、普通跑仍保存）连同各自需要的 harness 改动写进该题 NOTES 的 Grading note。

---

## 3. S-A：NOTES / 文档数字失实（21 处，逐条从 fixture 实算复核）

每条都用 python 从 fixture 重算过，不采信审阅报告的数字。其中 **2 条与审阅报告的说法不同**，以实算为准。

| 题 | v1 的说法 | 实算 | 处理 |
|---|---|---|---|
| tab-0005 | "the Ellwood site only (230.0)" | Ellwood 三人合计 **398.25**；Ellwood+Outbound 133.75；Ashford+Outbound 606.75 | 换成三个真实近似读法 |
| tab-0009 | "两行恰好等于下限"（BWO-1310 26/25、BWO-1501 75/25） | **无一行等于阈值**；含等号读法同样得 7 | 改写为「边界读法不影响结果」，最近的两侧各举一例 |
| tab-0010 | "KMD-2186 at 25 against 25" | 实为 **31 对 25**，且无一行等于阈值 | 同上 |
| tab-0019 | 三处翻转只列了两个月份 | 07-03-2026 月先读是 **3 July** | 补 July；并补「14-03-2026 无月先读法，退回日先读」——不写这条，decoy 是 5 而不是登记的 6 |
| tab-0020 | 月先读只翻转 2 行 → 57103.50 | **翻转 4 行**（INV-7748 −1265.50、MTR-2605 −735.80、INV-7784 +3375.00、MTR-2671 +1045.00），算式闭合到 57103.50 | 四行逐条列出并写出算式 |
| log-0006 | 重复段 11:42:26–**13:55:47** | 实为 11:42:26–**13:48:22**（18 行，逐字节相同，位于文件末尾） | 订正 |
| log-0007 | decoy "three hours earlier" | 11:41:18 vs 13:52:17 = **2 小时 11 分** | 订正 |
| log-0008 | verify.py docstring "07:26 to 11:19" | 实为 **07:31:36 → 10:54:22**（68 条） | 订正 |
| log-0011 | CART_LOCK_TIMEOUT 是 "louder"（4 条） | CART **4** 条、PG_CONN_RESET **5** 条 | 去掉 louder，两个计数都写明 |
| log-0012 | — | 首行同症状 502 可导出 `2026-09-28 16:12:30` | 在 uniqueness 段写明这是未登记的可导出错答案 |
| log-0016 | 引证 id `e07e0147a` | 实为 **`e0147a`** | 订正 |
| log-0017 | "the 09:47-style record at 11:47:02" | 自相矛盾的陈旧措辞 | 删 |
| log-0018 | decoy 在 "15% mark" | 第 **46/388** 条 ≈ **11.9%**；FATAL 在第 259 条（66.8%） | 订正并补 FATAL 位置 |
| log-0020 | "417 records" | 缩量后 **399** 条；首个 GATEWAY_STALL 在第 152 条（38.1%，原文的 38% 正确） | 订正 |
| scr-0008 | hidden 缺失行 "6 of 11" | 实为 **5 of 11**（S-3402/3405/3408/3423/3432） | 订正并逐条列出 |
| scr-0011 | decoy 报表是可见三份的汇总，"cannot show STR-6602" | **判分期 hidden 已写入工作区**，脚本自己的 glob 会读到它：真正的 decoy 是 STR-4407 45615 / STR-5120 76180 / **STR-6602 24950** / STR-8813 189700 / total **336445** | 换成判分期的 decoy，并把可见三份的数字单列为「开发期所见」 |
| scr-0012 | "four of the nine invoices" | 可见数据共 **10** 张发票，被丢弃 **6** 张（4 张列分隔 + INV-7408/INV-7422 两张带引号） | 订正 |
| scr-0015 / scr-0016 | hidden 被排除是因为「过了条数上限」 | hidden **根本不在模型的工作区里**（只写进判分沙箱）；判分期它在第 3 层目录下，默认 `max_depth=3` 也够不到；200 条上限遮住的是**可见** spool 的尾巴 | 三件事分开写清 |
| scr-0018 | 逐文件去重「仍落在该 decoy」 | 逐文件去重得 Chicory 64 / Kale 203 / Rhubarb 114 / Spinach 209 / **total 590**，既不是正解 468 也不是行计数 decoy 659 | 补出第三种错误输出 |
| fs-0007 | 「读列表里第一个同名匹配」也得 decoy | 两份都叫 `body_flow.csv`，**nettlewick 字典序在前**，取第一个恰是正解 | 删掉这条不成立的路径并说明原因 |
| fs-0008 | "200 页止于 arena-11"、"558 文件在 depth 2" | 200 条止于 **arena-05**（`surveys/arena-05/hx05-012.tsv`）、500 条止于 arena-11；555 个文件在**第 3 层** | 两处订正 |
| hyb-0007 | 引用 README 的 "frozen-mirror rule" 排除预览版 | README **没有**这条规则 | 改为由发布页自己的 stable/preview 分类 + 题面要 supported stable 来定唯一性 |
| hyb-0011 | "the request, the README and the zone notices all fail to identify one" | README **确有** "usually opened against the most recent billing period on file" | 见 §4 |

---

## 4. S-B 与三条额外公平性修正

**S-B（判据宽容度，题侧，不动 scorer）**

| 题 | 改动 | 版本 |
|---|---|---|
| web-0009/0010/0011/0012 | 单条小写 needle → `output_contains_any` 三种大小写形（`sealbreak` / `Sealbreak` / `SEALBREAK` 等） | +1 |
| web-0014 / web-0016 | `output_equals` → `output_equals_any`，容下 `7.4.1 (2026-08-19)` / `5.1.0 (2026-08-27)`（理由见 §0③） | +1 |
| nt-0007 | `git blame` → 兼收 `git annotate`（同一命令的另一个 porcelain 名）及大小写形 | +1 |
| code-0007 | 单 token `finished` → `output_contains_any`：字面值，或「两个值不匹配」的显式说法。**没有**采用报告建议的双 token（schema 表达不了「(finished\|Finished) 且 (completed\|Completed)」这种 AND-of-OR，而单要求 `completed` 是题面自带的免费 token） | +1 |
| code-0008 | 同上：`find_reference` 或「从未调用查询」的显式说法 | +1 |
| cfg-0014/0015/0016 | 整段 needle 加固（见 §0②） | +1 |

**额外三条**（逐题表里点名、不在 §7 处理清单上，但都是公平性而非文档问题）

1. **log-0006（v1→v2）**：`docs/billing-ops.md` 的 "The gateway has no request retries of its own: one line means one request." **正面为 decoy 88 背书**——按这句话，数行数就是对的。改为「它从不把同一行写两次；夜间归档拷贝此前有过重叠」，这才是解开重复段的那条规则。
2. **hyb-0006（v1→v2）**：`expect.tools: []` 是**零调用契约**，与参考解的 3 步工作区调用直接矛盾，每次通过都在按一份本题没有的契约记账。改成 `forbidden_tools: ["web_search", "web_fetch"]`——TR-NOTOOLNEED 在这题的含义就是「pin 已经在 deps.lock 里，上网找才是失败」。报告建议的 `max_calls: {web_search: 0}` **行不通**：加载器要求 budget ≥ 1，写 0 会让整题非法。
3. **hyb-0011（v2→v3）**：README 的 "Reconciliations are usually opened against the most recent billing period on file." 让「不反问、直接按最近季度作答」变得有据可依，而 turn-1 收紧后正是要判它挂。删掉该句（改为「每次对账针对对方点名的账期」）。decoy 75174.80 不受影响——2026-Q2 仍是台账里最新的一行。

---

## 5. 闸门与状态

```
lint.py            152 case(s) checked, 0 violation(s)
test_lint.py       8/8 OK
verify_all.py      152/152 PASS   （warning 分布与返修前逐题一致：
                                    verify_shape_unknown 43、sabotage_skipped_no_files 18）
dedup.py           no near-duplicate pairs flagged
coverage.py        无缺口，L0/L1/L2 = 38/76/38
web_hitcheck.py    16/16，5/5 phrasings
既有 40 题          git diff 为空
```

**status 未动**：88 draft / 64 reviewed 保持原样。置 `reviewed` 的依据（§5）是两道闸门 + 批次报告，闸门① 在 B2–B5 上仍未跑完；而且本轮的返修**发生在** B1 那次闸门之后。

**需要主控注意：4 道已 `reviewed`（B1 批，闸门①已实测）的题在本轮被改动**，它们的闸门读数是在 v1 上测的：

| 题 | 改动性质 | 是否影响 B1 读数 |
|---|---|---|
| tab-0008 | fixture（页眉多一行、README 一句） | 会：题面信息变了，需重测 |
| log-0006 | fixture（ops 文档一条规则） | 会：唯一性依据变了，需重测 |
| nt-0007 | 仅判据放宽 | 只会更宽松，旧的通过仍通过 |
| tab-0006 | 仅 NOTES | 不影响 |

## 6. 移交给工具轮（本轮冻结，未动）

1. **`FileExpectation` 缺 `excludes`**（或一个容忍结尾换行的 `equals`）：cfg-0013/0014/0015/0016 的「且仅此而已」判不到；cfg-0015 的「注释不复制进合并结果」同因判不到。
2. **`verify_all` 只收集三种 expect 形状**：43 题的 expect↔verify 互证与破坏测试结构性空转（本轮又因此把 web-0014/0016 的判据退回 equals 家族）。补 `output_contains` / `output_contains_any` 收集即可解锁。
3. **`RunExpectation` 只带一次调用、且判分副本用后即删**：scr-0019 的两条承诺判不到（dry-run 不落盘、普通跑仍保存），scr-0007 的 `--gross` 分支同理只能靠规格钉死、无法执行。

*报告生成：2026-09-22，扩量审阅返修轮。*
