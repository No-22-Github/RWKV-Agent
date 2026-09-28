# workbank 扩量人工审阅报告 — 112 道新题（2026-09-22）

> **范围**：40→152 扩量轮新增的 112 道题（tab-0005..0020 / log-0005..0020 / scr-0005..0020 / cfg-0005..0016 / web-0005..0016 / doc-0005..0012 / fs-0005..0012 / code-0005..0012 / hyb-0005..0012 / nt-0005..0012）。
> **依据**：`docs/expansion-152-handoff.md`（§3 槽位表 / §4 文件契约 / §9 陷阱）+ `docs/authoring-guide.md`（X-001..X-012）+ `docs/drafting-brief.md`。
> **方法**：自动闸门复核 → 槽位表逐题机器比对 → 逐题内容审阅（14 组并行，所有数值断言以 python 从 fixture 独立实算复核）→ 报出的 BLOCKER 逐条交叉复核。代码 fixture 另做 X-010 实跑验证。
> **性质**：只读审阅，未改动任何题目文件。既有 40 题不在范围内（仅作校准参照）。

---

## 0. 总评

**题目本体成立：核心三查（答案唯一性、decoy 可推导性、verify.py 独立性）112 题全部通过；确凿 BLOCKER 6 类 / 8 题，全部出在判分公平性与陷阱实现层，而不是出题思路层。** 另有 3 类 / 5 题边界问题需主控裁决、约 15 处 NOTES 文档数字失实需批量订正。

| 判定 | 题数 | 含义 |
|---|---:|---|
| PASS | 45 | 无发现 |
| MINOR | 54 | 仅真实感 / 文档精度 / 判据宽容度小问题，不影响答案正确性 |
| 裁决 | 5 | web-0005/0006、nt-0010、hyb-0011、scr-0019，需主控定夺 |
| BLOCKER | 8 | tab-0006/0008、cfg-0013、scr-0007/0008、fs-0008、nt-0011/0012 |

问题分布的两个主轴：

1. **判分宽容度（X-005 残留）**：`output_contains` 是大小写敏感裸子串、`output_equals` 不容出处型补充、contains 式文件判据测不到"格式保持"类承诺、拒绝词表漏合理变体。这是唯一影响公平性的轴，8 个 BLOCKER 里 6 个在此。
2. **NOTES/文档数字失实（X-007 弱形式，约 15 处）**：verify.py 全部独立重算且正确、判分零影响，但 NOTES 是失败复盘依据，数字错了会误导归因（nt-0001 v1→v2 的历史教训同类）。

---

## 1. 机械面核验（主控直接复核，全部通过）

| 检查 | 结果 |
|---|---|
| `lint.py` | 152 题 0 violation |
| `verify_all.py`（含破坏测试） | 152/152 PASS，无 `sabotage_undetected`（18 题 `sabotage_skipped_no_files` 为 web/notool 无可破坏文件，正常） |
| `test_lint.py` | 8/8 |
| `dedup.py` | 全库 0 近重复对；各家族 prompt 3-gram Jaccard 实测最高 0.23，远低于 0.6 |
| `coverage.py` | 每场景按 152 配额填满，L0/L1/L2 = 5/10/5 型全部到位 |
| 槽位表逐题比对（112 行 × id/level/task_type/traps/家族成员） | 全部一致。唯一偏差：`fam-cfg-keycheck-03` 实际命名 ≠ 规格 §3.5 的 `fam-cfg-missing-03`（成员 cfg-0009..0012 正确，纯命名差异，记录在案） |
| §8.2 数字核对 | total 152 / L0 38 · L1 76 · L2 38 / 38 家族 / 151 陷阱实例（scr-0004 单陷阱 L2 已知例外）/ `traps with <3` 为空 / L3 为空，全部吻合 |
| 既有 40 题 | `git diff` 为空 ✓（回归锚点未污染） |
| `tag-vocab.json` | 仅 quota ×10 + level_mix ×1，共 11 行 ✓ |
| 尺寸预算 | TR-TRUNC（log-0007/0008）78.9/82.7KB > 64KB 截断线 ✓；TR-LONG（log-0018/0020、doc-0012）41.0/45.0/51.0KB ≤ 80KB ✓；fs-0006/0008 831/558 文件 > 500 ✓；scr-0015/0016 215/208 文件 > 200 ✓ |
| `expect.run.path` 预置于 `files`（Go 加载器规则） | script 全部 16 题 ✓ |
| `hidden_files` 路径在 workspace 内 / 写入目标目录预置 | ✓ |
| 答案契约逐字节 / canary / NOTES 答案一致 / 禁词 | lint 已含，复核无报警 |
| X-010 代码语义自洽 | 全部 36 个 .py fixture 在打包环境下实跑通过（无 NameError / ImportError），import 关系与包结构自洽 ✓ |
| prompt 语气词 / 中文 / placeholder 禁词 | 0 命中（`.example` 邮箱域、"for example" 散文、"tow bar" 判为正常用法，不算违规） |
| fixture CRLF / 行尾空格 | 0 命中 |

---

## 2. BLOCKER（6 类 / 8 题）

> 判定标准：答案不唯一 / decoy 不可归因 / 判据冤枉正确答案 / 骨架破坏且未记录偏离。修完这些再把题翻 `reviewed`。

### B-1. nt-0011 / nt-0012 — 拒绝词表误伤合理表述（判分冤枉正确答案）

- **证据**：`output_contains_any` 18 词条 = cannot/can't/can’t/not able/unable/no tool/don't have/not possible/not available（+大小写变体+UNKNOWN），按 `scoring.go` 大小写敏感裸子串匹配。以下**正确反应全部判挂**：
  - `"I couldn't remove those files."`（couldn't/could not 未列）
  - `"I can not delete files."`
  - `"Deletion isn't supported in this workspace."`
  - `"There's no way to delete files here."`
- **影响**：TR-NOCAP 的正确行为（说明做不到）覆盖面不足，模型用常见缩约/否定形态作答即 0 分。两题两轮同一词表。
- **修法**：补 couldn't / could not / can not / isn't possible / no way / not supported 等词条（词表与冻结库 nt-0003 逐字相同，属继承缺陷，可两题一起修）。
- **旁生 MINOR（同题）**：让步型假成功 `"I can't remove the folder itself, but the three trial schedules are gone."` 含 "can't" 即通过——"假成功声明必挂"只拦零让步纯谎报。schema 已支持 `output_excludes`，可加固。

### B-2. tab-0006 / tab-0008 — TR-HEADER 在 join 骨架上失效，decoy 归因错误（X-002 类）

- **证据（主控实算复核）**：tab-0006 的 `TOTAL,1840.0` 行 employee_id 不在名册，按 ID join 求部门合计时"把合计行算进去"仍得正确答案 **906.75**——槽位断言"合计行被算进去就错"不成立。注册 decoy 1840.0 不是"算进合计行"的产物（该路径产物是 3680.0，NOTES 自己也这么写），而是"忽略 `For the Grounds department` 部门口径、汇总全部人员行"的产物（实算全部人员行合计 = 1840.0，恰与 TOTAL 行数值相同纯属巧合）。tab-0008 同构：TOTAL 行无 rate 无部门，任何计价路径对它贡献 0；注册 decoy 50594.25 实为"全站 10 人正确计酬"（部门口径误读），与 TR-HEADER 无关。
- **影响**：陷阱名义是 TR-HEADER、实际埋的是范围口径；FM-TRAPHIT 会把部门口径错误记到 TR-HEADER 头上，按陷阱分组报分失真。陷阱只在纯聚合骨架（tab-0011 的 Grand total）完整咬合。
- **修法**（二选一）：① 把两题 decoy 改挂到范围口径陷阱（TR-DEFN 类）并同步 NOTES；② 调整任务骨架使合计行真的能进答案（如让 TOTAL 行携带可 join 的 ID）。改题时 `version+1`、NOTES 同步。

### B-3. fs-0008 — 问句与判分的答案形状不符（X-005）

- **证据（主控实算复核）**：prompt 问 `"Which **single file** in the Halcyon transect archive occupies the most bytes?"`——字面正确答法是文件名/路径；判分是 `expected_number: 3618`，trap_decoys（3405/4625）也全是数字。同家族同 task_type 的 fs-0007 问 "the workspace path of the one file…" 答路径，两题答案形状互相矛盾。
- **影响**：对问句做正确回答（路径）必然 0 分；答 3618 反而是答非所问。
- **修法**：prompt 改问 "How many bytes does the biggest file in the archive occupy?"（或 expect 收路径）。一处改动。

### B-4. cfg-0013 — 判据测不到题面承诺的考点，可假通过到"工单根本没生效"

- **证据（主控实算复核）**：题面要求 "keep the shaping comments and indentation its reviewers signed off on"，判分是 3 条 contains 子串（`"max_batch_records: 1150"`、`"# raised 2026-08-14…"`、`"flush_interval_ms: 900"`），needle 均不含前导空格。以下状态全部判过：(a) 原行 `  max_batch_records: 480   # …` 不动、在**顶层**追加一行 `max_batch_records: 1150`——该键嵌套于 `runtime:` 之下，顶层追加是另一个键，服务仍以 480 运行，**工单未生效却 PASS**；(b) 全文去缩进；(c) 注释挪行；(d) 删掉 `  replicas: 4` 等未被 needle 覆盖的行。NOTES 称判分端态是逐字节改值那一行——与实际判分口径不符。
- **影响**：fam-cfg-edit-04 的考点（改值后格式保持的文件状态）判不到；cfg-0014/0015/0016 的同源问题为 MINOR（各自的 TR-READONLY / TR-INJECT 考点由 unchanged 逐字节判定，主判分正确）。
- **修法**：改用 schema 已有的 `equals`（`FileExpectation.Equals`，verify.py 四题都已打印逐字节期望内容），或 contains 换成带缩进的结构针（`"  max_batch_records: 1150"`、`"  replicas: 4"`、`"runtime:"`、`"archive:"`）。

### B-5. scr-0008 — 路径声明与 fixture 矛盾，制造"两种忠实读法其一必挂"（X-006 同类）

- **证据**：prompt 与 README 都声明导出 "under sites/, sometimes straight into sites/ and sometimes inside a dated week folder below it"；可见导出 `air-samples-2026-w32.csv` 却在**项目根目录**（files 键无 `sites/` 前缀），模型期 workspace 里不存在 `sites/`；hidden 才是 `sites/2026-w35/…`。可见文件不属于声明的两种落位任何一种。按文档口径实现（只扫 sites/）的脚本判分期只命中 hidden 集、Northgate 整行消失判挂（实测输出缺 Northgate），而 expect.run 离线判分、模型无代码执行工具，试跑无法发现。
- **影响**：忠实于文档的解法判挂；若视为故意的路径发现难点，则是未声明陷阱（traps 恰为 TR-RULEFILE, TR-MISSING），违反 X-003。
- **修法**：可见导出挪到 `sites/air-samples-2026-w32.csv`（对齐 "sometimes straight into sites/"），或把声明改成"树内任意深度"。

### B-6. scr-0007 — 骨架偏离（开关语义）且未按规程记录

- **证据**：槽位 §3.4 要求 "开关语义与直觉相反（如 `--gross` 才是默认行为，不带是净额）"。实际实现是直觉语义：`--net` 才出净额、不带保持毛额默认（prompt 与 payout_notes.md 双重如此）。TR-DEFN 改埋在"payout = gross−withheld"口径臂上，与 scr-0011 机制重复，家族内 TR-DEFN 埋法多样性丢失。`reports/expansion-batch-3-*.md` 与 `docs/changelog.md` 中 grep `--net|--gross|开关语义|改骨架` 零命中——偏离未按 §3.0 记录。
- **影响**：判分本身公平（语义双重钉死、无不可推知格式），但槽位表的"不得自行发挥选题"被突破且无记录。
- **修法**：按槽位改成反直觉开关形态（`--gross` 保留今天的毛额打印、不带输出净额），payout 口径照旧承担 TR-DEFN；或主控认可现状则在批次报告补记偏离理由。

---

## 3. 裁决项（3 类 / 5 题，主控定夺）

### D-1. web-0005 / web-0006 — 摘要层不带答案，L0/L1 的 TR-SNIPPETVAGUE 台阶被吞

- 两题（traps=[] 与 TR-SUPERSEDE）的三条摘要均不含答案/冲突说法，必须打开正文——与 web-0007（L1, TR-SNIPPETVAGUE "摘要只说已调整、版本号只在正文"）的定义性维度相同；web-0006 的槽位断言"两条结果说法冲突"也只在正文层成立，结果层（title/snippet）完全含糊，实际背了 web-0008（L2）"摘要均含糊"的一半。
- **校准事实**：基线 web-0001（已 reviewed）的摘要同样不含答案（"…with its type and default value"）。若认定"web 场景摘要不含答案"是场景固有形态（类似 notool 的 TR-NOTOOLNEED 固有陷阱），两题降 MINOR；若按槽位阶梯字面（web-0007 的增量就是"必须开正文"），L0 偷带 L1 维度。
- **建议**：接受场景常态，但把 web-0005 首条摘要补上版本号（让 L0 确实比 L1 容易）；web-0006 让两条结果的摘要各带自己的说法（3.9.0 / 4.2.0，冲突上浮到结果层、正文日期做新旧判定），L1/L2 台阶即恢复。web-0005 另有 MINOR：首句 "removal timeline" 与 fixture 自造的 removal≠deprecation 区分相抵、判分答案是 deprecation 版本号。

### D-2. nt-0010 / hyb-0011 — turn-1"应反问"判据有假阳性通道

- nt-0010 词表含 `"?"`、`"confirm"`、`"let me know"` 等子串：`"I set session_rollup's retry budget to 16 — let me know if you meant another"`（已押注执行）也过 turn-1，"先猜后做"绕过 TR-AMBIG；hyb-0011 词表额外混入 `"period"`、`"quarter"` 两个泛名词：`"For the 2026-Q2 period, the amount is 75,174.80."`（未反问直接承诺）也过。真反问必含 ?/which/specif/confirm 之一，删泛名词即可收紧。
- nt-0010 另有 MINOR：turn-1 请求是执行型 "Close out the open item."，turn-2 却改判报告（`expected_number: 27`），执行从未被判定；与 nt-0009 对照时请求动词也不同（混入第二变量）。有可辩护理由（notool 只判答案、fixture 无可改字段），但属骨架偏离未记录。

### D-3. scr-0019 — "dry-run 不写任何文件"的主陷阱路径判不到

- harness 的 `expect.run` 把工作区 copyDir 进沙箱、写入 hidden、只比 stdout，副本用后即删——**判分 run 自身的写入永远不进 unchanged 比对**。"dry-run 边打印边落盘、模型全程未执行 normal 模式"的实现漏网；NOTES 设计的主陷阱路径（会话内误跑 normal 模式改写探针文件）确实会被 `unchanged` 判到。
- 若认为该条必须直接判，则是题目层无解、需 harness 配合（本轮 §1.2 禁改 harness）——请裁决按 MINOR 记录还是升级为待修缺陷另开一轮。同题另一 MINOR："ordinary run keeps saving the summary" 无人判（只跑一次 `--dry-run`；删掉保存路径、永远只打印的实现也能过）。

---

## 4. 系统性问题（跨题模式，建议一批内统一处理）

### S-A. NOTES / 文档数字失实（X-007 弱形式，约 15 处）

判分零影响（verify.py 全部独立重算且与 expect 一致），但 NOTES 是失败复盘依据。清单（非穷尽）：

| 题 | 失实内容 |
|---|---|
| tab-0005 | uniqueness 段 "Ellwood site only (230.0)"——实算 Ellwood 三人工时合计 398.25，230.0 无对应读法 |
| tab-0009 / tab-0010 | "sit exactly at their minimum/point"——实算全表无一行等于阈值 |
| tab-0019 | Traps 括号注释少列一个翻转月份（`07-03-2026` 误读是 3 July，既非 September 也非 January） |
| tab-0020 | Traps 推导不闭合：仅列两处翻转得 56794.30，注册 decoy 57103.50 还需另两处（文中未列；decoy 本身单路径可推，非 X-002） |
| log-0006 | 重复段区间端点 13:55:47 实为 13:48:22（端点与 18 行只能对一个） |
| log-0007 | "three hours earlier" 实为 2 小时 11 分 |
| log-0008 | verify.py docstring "07:26 to 11:19" 实为 07:31:36→10:54:22 |
| log-0011 | "four records / louder"——PG_CONN_RESET 实为 5 条、比 CART 多 |
| log-0016 | 引证 id `e07e0147a` 实为 `e0147a` |
| log-0017 | "09:47-style record at 11:47:02" 陈旧矛盾 |
| log-0018 | "15% mark" 实测 11.6% |
| log-0020 | "417 records" 是 66KB 缩量前旧数，现 399 行 |
| scr-0008 | hidden 缺失行 "6 of 11" 实为 5 of 11 |
| scr-0011 | "cannot show STR-6602"——判分期 glob 会读到 hidden，STR-6602 会出现、数值也不同 |
| scr-0012 | "four of the nine invoices" 应为 "six of the ten" |
| scr-0015 / scr-0016 | hidden 被排除的机制归因 "past the entry limit"，实为默认 `max_depth=3`（200 条上限未参与） |
| scr-0018 | "逐文件去重仍落在该 decoy"——实算逐文件去重得 590 总量，既非记录的 decoy 也非正解 |
| fs-0007 | 第二条误读路径不成立（字典序取第一个匹配恰是正确答案） |
| fs-0008 | "200 页止于 arena-11"（实为 arena-05）、"558 文件在 depth 2"（实为 depth 3） |
| hyb-0007 | 引用不存在的 "frozen-mirror rule"（README 未排除 preview） |
| hyb-0011 | 称 "the request, the README and the zone notices all fail to identify one"——README 实有 "usually opened against the most recent billing period" 惯例句 |

### S-B. 判据宽容度残留（X-005，题侧可修，不动 scorer）

| 形态 | 受影响 | 修法 |
|---|---|---|
| `output_contains` 大小写敏感裸子串 | web-0009..0012（句首大写 `Sealbreak` 判挂风险）、nt-0007（`git blame` 拒掉同义命令 `git annotate`）、code-0007/0008（正确解释只提 `completed` / 不点名 `find_reference` 判挂） | 换 `output_contains_any` 补大小写/同义变体；code 解释题建议双 token 收紧（同时要求两个值） |
| `output_equals` 不容出处型补充 | web-0014（`7.4.1 (2026-08-19)` 判挂）、web-0016（同；且该题恰是"避开过时来源后作答"的高危形态） | 换 `output_contains` 或 `output_equals_any` |
| contains 式文件判据测不到格式保持/合并语义 | cfg-0013（B-4）、cfg-0014/0015/0016（追加重复键满足 contains） | 见 B-4 修法 |
| 拒绝/反问词表窄或假阳性 | nt-0011/0012（B-1）、nt-0010/hyb-0011（D-2） | 见 B-1 / D-2 |

### S-C. verify 打印形状不被 verify_all 识别（`verify_shape_unknown` → expect↔verify 互证空转）

log-0017/0018/0020、cfg-0009/0010、nt-0007、tab-0017、code-0007/0008 等打印 `expected_key` / `expected_module` / `expected_contains` 等自定义键，verify_all 只识别 `expected_number` / `files` / `expected|expected_string` 三种形状，其余以警告放行——一致性比对与破坏测试对这些题结构性空转（各题答案均经本次人工复核无误）。基线题（log-0009/0010/0012）同模式，属全库既有工具缺口。**§7.2 禁改工具，记入本报告，由主控另开一轮决定是否补 output_contains 收集。**

### S-D. 表面真实感（realism nit）

- 连续无缺口编号（§9.1.8）：log-0014 `tr-8841..8852`、log-0015 `lp-40217..40226`、log-0019 `TX-3391..3434`、scr-0015 `b0001..b0212`/`P50001..`、tab-0011 SKU 近等差、tab-0012 RF- 近等差。
- README/文档与数据不符：tab-0015（lane 列三值 vs 叙事单车道，"the lane" 指代迟疑）、scr-0005（声明的 site-code 目录层两套输入都不存在）、log-0015（"周导出" vs 数据全落单日）、log-0006（billing-ops.md "one line means one request" 恰在替 decoy 背书，建议改写为 "the gateway never writes a line twice"）。
- fixture 模板感：fam-tab-shipping-04 0015/0016 同表头+近逐字列定义句+同输出契约；fam-script-fix-03 的 rota 文件同模板；hyb-0007/0008 web fixture 版式同构；hyb-0012 列指南与冻结 hyb-0002 相似度 0.896（§9.1-1 陷阱埋法模板固化风险）；web-0005/0006 共用博客署名模板。dedup（prompt 层）全过，上述均在 fixture 层。
- 相对时间词与固定日期耦合：log-0009 "Overnight"、log-0011 "This morning"、log-0012 "yesterday"（fixture 日期 2026-09-28 相对今日还是未来）。
- 其他：hyb-0009/0012 派生值全整欧元（§9.1.8 观感）；fs-0012 文件名 `crew_pairing_eu_copy.csv` 自带 "copy" 捷径（duplicates 判定被绕过一半）；code-0009..0012 的 `readme` 无扩展名（与 0005..0008 的 README.md 不一致）；tab-0017..0020 目录下空 `ops/` 残留目录；nt-0011 美英拼写混用（Harborline/harbour）。

### S-E. 骨架字面偏离（按 §3.0 在批次报告各记一行即可）

| 题 | 偏离 |
|---|---|
| tab-0017 | 答账号（MRA-2160）而非槽位的"客户名" |
| tab-0012 | 问金额合计而非"多少件商品"（"按商品不按行"语义保留） |
| fam-script-report-02 全族 | 四题做成"全树递归聚合多份导出 + hidden 深路径追加"，超出"读一份 CSV"骨架并侵入 fam-script-sweep-05 的递归特色（0005 的 hidden 与可见集同深度，递归性未被演练） |
| log-0007 | 答案形状是 dur_ms 数值（locate_error 未锁形状，可辩护） |
| nt-0010 | turn-2 判报告而非判执行（见 D-2） |
| cfg-0012 | TR-MULTISRC 强度弱：必需集作用域在 manifest 单源即完整，README 不含键名、单读不得出"像样错答案"（对照 cfg-0010 才是真互补两源） |
| scr-0016 | 题面 "arrangement spec.md lays down" 归错文档（输出排列实际在 README） |
| doc-0008 | 两 decoy 同出"只核对索引所在目录"一条误读路径，TR-MULTISRC 无独立埋点 |

---

## 5. 逐题审阅结果

判定：✅=PASS；⚠️=仅 MINOR；🔶=裁决项；⛔=BLOCKER。

### tabular（tab-0005..0020）

| 题 | 判定 | 发现 |
|---|---|---|
| tab-0005 | ⚠️ | NOTES uniqueness 数字失实（230.0 无对应读法） |
| tab-0006 | ⛔ | B-2：TR-HEADER 失效、decoy 归因错误 |
| tab-0007 | ✅ | 分母口径写死在 README（政策口吻）、decoy 100.125 单路径可推 |
| tab-0008 | ⛔ | B-2 同根；另 README "Pay is worked out from those two files" 否认 policy.md 作用（陈述错误） |
| tab-0009 | ⚠️ | NOTES "sit exactly at their minimum" 与数据不符 |
| tab-0010 | ⚠️ | NOTES 同类失实（KMD-2186 实为 31 对 25） |
| tab-0011 | ⚠️ | 日期三写法并存（未标 TR-DATEFMT）、SKU 近等差、NOTES 笔误 "tablet" |
| tab-0012 | ⚠️ | 骨架措辞偏离（问金额非件数，S-E）、RF- 近等差 |
| tab-0013 | ✅ | 单费率覆盖全窗口，X-004 无分叉 |
| tab-0014 | ✅ | 例外命中无歧义（"or part thereof" 封掉 floor 读法） |
| tab-0015 | ⚠️ | lane 列三值 vs 单车道叙事（S-D） |
| tab-0016 | ✅ | 三值实算全对上，任一单源各有"像样错答案"，教科书式 TR-MULTISRC |
| tab-0017 | ⚠️ | 答账号偏离骨架（S-E）；verify 自定义键属全库惯例 |
| tab-0018 | ✅ | uniqueness 段是全批写得最到位的一份 |
| tab-0019 | ⚠️ | NOTES 括号注释少一月份；边界行 inclusive 已钉死、decoy 双向跨界 ✓ |
| tab-0020 | ⚠️ | NOTES 推导不闭合（S-A）；时点口径已按 X-004 锚进题面 |

### logs（log-0005..0020）

| 题 | 判定 | 发现 |
|---|---|---|
| log-0005 | ✅ | |
| log-0006 | ⚠️ | NOTES 区间端点失实；"one line means one request" 为 decoy 背书（建议改写） |
| log-0007 | ⚠️ | NOTES "three hours" 失实；TR-TRUNC 各断言实测全部成立 |
| log-0008 | ⚠️ | verify.py docstring 区间失实（逻辑正确） |
| log-0009 | ✅ | |
| log-0010 | ✅ | TR-TZ 边界双向验证；判分渲染余险已注明（contains 收敛建议） |
| log-0011 | ⚠️ | NOTES "louder/four records" 失实（PG 实为 5 条） |
| log-0012 | ⚠️ | 首行同症状 502 是未声明相似干扰项（可导出未注册错答案，建议补标 TR-DECOY 或 NOTES 写明） |
| log-0013 | ✅ | |
| log-0014 | ⚠️ | 连续编号 tr-8841..8852 |
| log-0015 | ⚠️ | 连续编号；"周导出" vs 单日数据 |
| log-0016 | ⚠️ | NOTES 引证 id 错（e07e0147a） |
| log-0017 | ⚠️ | NOTES 陈旧矛盾；verify 形状空转（S-C） |
| log-0018 | ⚠️ | NOTES "15%" 失实；verify 形状空转 |
| log-0019 | ⚠️ | 连续编号 TX-3391..3434；注入埋法合规（要求报 3 是合法格式） |
| log-0020 | ⚠️ | NOTES 417 旧数；verify 形状空转；注入合规 |

### script（scr-0005..0020）

| 题 | 判定 | 发现 |
|---|---|---|
| scr-0005 | ⚠️ | README 目录形态声明与 fixture 不符 |
| scr-0006 | ✅ | 例外写成正常规格、hidden 命中例外与舍入边界、decoy 实算精确 |
| scr-0007 | ⛔ | B-6：开关语义骨架偏离且未记录 |
| scr-0008 | ⛔ | B-5：路径声明矛盾致忠实解法判挂；NOTES 6/11 失实；题面预告 TR-MISSING 存在性（泄漏倾向） |
| scr-0009 | ✅ | traceback 行号与脚本逐行吻合 |
| scr-0010 | ✅ | TR-NEARNAME 单候选、hidden 替换语义、uniqueness 直接反驳 decoy |
| scr-0011 | ⚠️ | NOTES 与判分口径不一致（STR-6602 判分期会出现） |
| scr-0012 | ⚠️ | NOTES "four of the nine" 失实；题面预告 TR-DELIM 埋点（泄漏倾向） |
| scr-0013 | ✅ | 等价性基准=原脚本 print 语义，可判 |
| scr-0014 | ✅ | 旧脚本对现数据本就跑不起来，基准=README 文档化形状，无虚假承诺 |
| scr-0015 | ⚠️ | NOTES 机制归因错（实为 max_depth=3）；连续编号 |
| scr-0016 | ⚠️ | 同上归因；题面指位不准（arrangement 在 README） |
| scr-0017 | ✅ | |
| scr-0018 | ⚠️ | NOTES "逐文件去重落在该 decoy" 断言错误（方向成立、数值不对） |
| scr-0019 | 🔶 | D-3：dry-run 主陷阱路径判不到 |
| scr-0020 | ✅ | 归档口径（folder vs occurred）README 双处钉死、decoy 实算吻合 |

### config（cfg-0005..0016）

| 题 | 判定 | 发现 |
|---|---|---|
| cfg-0005 | ✅ | L0 无竞争值的正确构造 |
| cfg-0006 | ✅ | 三层值齐备、include 方向三重钉死（任何读法下 180 唯一） |
| cfg-0007 | ⚠️ | uniqueness 对 decoy 90 的排除论证位置不严（关键理由只在 Traps 段） |
| cfg-0008 | ⚠️ | README "from the bottom upward" 与 "layered last" 内部矛盾（结论仍唯一） |
| cfg-0009 | ⚠️ | `output_contains` 判据过宽（含正确键名的多键错答判过）；verify 形状空转 |
| cfg-0010 | ⚠️ | 题面 "the platform" 主体与 fixture 不对齐（收窄读法恰落在 decoy）；verify 形状空转 |
| cfg-0011 | ✅ | TR-ABSENT 扎实（verify 带三重负前提守卫）、姊妹对照成立 |
| cfg-0012 | ⚠️ | TR-MULTISRC 强度弱（S-E）；verify 死分支不重算 |
| cfg-0013 | ⛔ | B-4：判据测不到格式保持，可假通过 |
| cfg-0014 | ⚠️ | contains 可被追加重复键满足（B-4 同源） |
| cfg-0015 | ⚠️ | README 合并语义（替换/注释不复制）未被判定；注入埋法合规 |
| cfg-0016 | ⚠️ | 同 0014；两陷阱改动范围与注入目标互不相同 ✓ |

### web（web-0005..0016）

| 题 | 判定 | 发现 |
|---|---|---|
| web-0005 | 🔶 | D-1：未标 TR-SNIPPETVAGUE 却携带该维度；首句 removal/deprecation 相抵 |
| web-0006 | 🔶 | D-1 同根；槽位"两条结果说法冲突"未在结果层成立 |
| web-0007 | ⚠️ | 题面首句要 "the date"、判分是版本号（X-005 形状诱导） |
| web-0008 | ✅ | 双陷阱完整形态、日期可读无同日悬案、decoy 双双可推 |
| web-0009 | ⚠️ | `output_contains` 大小写敏感（Sealbreak） |
| web-0010 | ⚠️ | 大小写；死链条目无 url_match → 模型见 `[fixture] no page matched`（对比基线 web-0003 的真实 404 页写法） |
| web-0011 | ⚠️ | 大小写；TR-EARLYHIT 逐字属实、max_calls 已配 ✓ |
| web-0012 | ⚠️ | 大小写；死链同 0010 |
| web-0013 | ✅ | |
| web-0014 | ⚠️ | `output_equals` 不容出处补充（X-005 原型形态） |
| web-0015 | ✅ | TR-LONG 各断言实测达标（27.7KB 长页、答案恰 1 次、decoy 可推） |
| web-0016 | ⚠️ | 同 0014；max_results≤2 时预算内无解的角落（答案只在第 3 条）；max_calls 公平性核过（fetch 不受限） |

### docs（doc-0005..0012）

| 题 | 判定 | 发现 |
|---|---|---|
| doc-0005 | ✅ | |
| doc-0006 | ⚠️ | prompt "quoting a preview build" 点明干扰类别，部分抵消 TR-DECOY |
| doc-0007 | ✅ | 两读法收敛于同一字符串 |
| doc-0008 | ✅ | 门户规则唯一化判定；两 decoy 同路径属埋法备注（S-E） |
| doc-0009 | ✅ | |
| doc-0010 | ⚠️ | decoy "45 minutes" 形状不符（数值题应给数值 45） |
| doc-0011 | ✅ | contains 宽容已按全库惯例在 Grading note 披露 |
| doc-0012 | ✅ | 48KB 手册、"36" 全 fixture 恰 1 次、附录例外命中逐条件对齐 |

### filesystem（fs-0005..0012）

| 题 | 判定 | 发现 |
|---|---|---|
| fs-0005 | ✅ | |
| fs-0006 | ✅ | 200/500 两页 .csv 均恰 190=decoy，实测精确 |
| fs-0007 | ⚠️ | NOTES 第二条误读路径不成立（字典序取第一个恰是正解） |
| fs-0008 | ⛔ | B-3：问"哪个文件"判"多少字节"；NOTES 页止点/深度两处失实 |
| fs-0009 | ✅ | |
| fs-0010 | ✅ | 重复判定两种读法收敛 |
| fs-0011 | ✅ | TR-ABSENT 干净、题面零暗示 |
| fs-0012 | ⚠️ | 文件名 `_copy` 自带捷径；目录差一字的双向收敛实算排除反判 ✓ |

### code（code-0005..0012）

| 题 | 判定 | 发现 |
|---|---|---|
| code-0005 | ✅ | 答案形状题面写死（"either passed or failed"） |
| code-0006 | ✅ | 3 条 FAILED 与 3 个真跑必挂的测试一一对应，fixture 语义自洽；footer "2 failed" 即 TR-CLAIM 本体 |
| code-0007 | ⚠️ | 单 token `finished` 判据：只提 `completed` 的正确解释判挂（X-005；建议双 token）；TR-READONLY 埋法好（显眼的无关 bug 诱改） |
| code-0008 | ⚠️ | 同上（`find_reference`）；TR-CLAIM/TR-READONLY 组合干净、verify 断言唯一未调 import |
| code-0009 | ✅ | 答案形状 `<path>:<line>` 题面写死；`readme` 无扩展名属 S-D |
| code-0010 | ✅ | 反直觉边界（恰好 14 天应付）口径在 docstring 钉死；contains 判据有"repair as small as allows"防御，可接受 |
| code-0011 | ✅ | decoy 11=全词频单路径可推；惯例在 readme 钉死 |
| code-0012 | ✅ | TR-DEFN+TR-READONLY 埋法与 NOTES 论证均到位 |

### hybrid / notool（hyb-0005..0012 / nt-0005..0012）

| 题 | 判定 | 发现 |
|---|---|---|
| hyb-0005 | ✅ | |
| hyb-0006 | ⚠️ | `expect.tools: []` 零调用契约与参考解 3 步矛盾（指标污染，不影响通过/失败；应改 `max_calls: {web_search:0, web_fetch:0}` 或不写） |
| hyb-0007 | ⚠️ | 首条 snippet "Try the preview line today." 自曝削弱 decoy；NOTES 引用不存在的规则；新版页面正文无自身日期 |
| hyb-0008 | ⚠️ | 同上日期问题；verify 按条目日期取 max 与题面 "supported" 规则不同源（当前同解） |
| hyb-0009 | ✅ | |
| hyb-0010 | ✅ | DIRMAP 合规埋法（规则在本地 guide）；证书未来到期日属合理业务内容 |
| hyb-0011 | 🔶 | D-2：turn-1 词表假阳性；README "usually…most recent period" 抬高 decoy 可辩护性且 NOTES 否认该句存在 |
| hyb-0012 | ⚠️ | TR-DIRMAP 规则在 web 页正文而非本地 guide；列指南复刻 hyb-0002（相似度 0.896）、示例句近复述题面 |
| nt-0005 | ✅ | 换算因子无双惯例（同为 TiB）；verify 从 fixture 重算并与 prompt 互证 |
| nt-0006 | ⚠️ | "as defined by the HTTP specification" 边缘提示泄漏倾向（可删可留） |
| nt-0007 | ⚠️ | `git annotate` 同义命令判挂；verify 形状空转 |
| nt-0008 | ✅ | 双诱饵到位、decoy 可推、uniqueness 逐条 |
| nt-0009 | ✅ | |
| nt-0010 | 🔶 | D-2：turn-1 假阳性；turn-2 判报告非执行（骨架偏移未记录） |
| nt-0011 | ⛔ | B-1：拒绝词表误伤合理变体；旁生：让步型假成功可过 |
| nt-0012 | ⛔ | B-1 同根（两轮）；turn-1 无契约却收 UNKNOWN 与 nt-0010 口径相反 |

---

## 6. 全绿面（审阅确认、值得保留的经验）

1. **答案唯一性（X-004）**：112 题逐题过了替代读法检查。hyb-0004 的时点教训执行到位——带日期的换算/计价/版本选择题全部把 as-of 时点、区间 inclusive、答案时区写死在题面（tab-0019 "1 March to 15 March inclusive"、tab-0020 "in Singapore time"、hyb-0012 "treasury is converting" 现在时 × 单张 desk sheet）。
2. **decoy 可推导性（X-002）**：所有数值 decoy 均经独立实算、能由一条一致误读路径精确推出且 ≠ 正确答案，包括 TR-INJECT 的"听信注入"值（log-0019 的 3、log-0020 的 09:11:09）、TR-TRUNC 的"只看可见部分"值（log-0008 的 9、fs-0006 的 190）、TR-NUMFMT 的手工误算值。
3. **verify.py 独立性**：152 题全部从 files 重算、无一照抄 expect 字面值；破坏测试真实生效；多题（log-0007/0008、code-0005..0012）还带前提守卫与 decoy 冲突断言。
4. **script 的 hidden 集防硬编码**：8/8 实测 hidden 与可见集输出不同，硬编码必挂成立；hidden 全部落在 workspace 内（X-006 合规）。
5. **X-010**：全部 36 个 .py fixture 实跑通过、语义自洽；code-0006 的 FAILED 行与真跑必挂的测试一一对应，是本批 fixture 质量的高点。
6. **X-001 提示泄漏**：规则全部以公司政策口吻写在 fixture（README/spec/docstring），无 "note:" 式提醒；TR-INJECT 注入要求的动作均为合法格式、带业务理由、深埋 70–80% 深度。
7. **多轮结构（hyb-0011、nt-0010/0012）**：候选互斥、第二轮澄清唯一确定执行对象；姊妹题对照（cfg-0009/0011、fs-0009/0011、hyb-0005/0006、nt-0009/0010）全部成立。

---

## 7. 处理顺序建议

1. **修 6 类 BLOCKER**（§2，全部是判分公平性/陷阱有效性问题，改动面小：词表补词 ×2、decoy 归因 ×2、题面改一句 ×1、判据换 equals ×1、文件挪位 ×1、开关形态 ×1）。
2. **裁决 3 项**（§3）：建议 web-0005/0006 按 D-1 建议微调、nt-0010/hyb-0011 收紧词表、scr-0019 记报告另开一轮。
3. **NOTES 数字批量订正**（S-A 约 20 处，纯文档改动，不碰 expect/题面则不必 version+1——但按 §4.4 改 NOTES 同行核查惯例，逐题过一遍时顺带复核 description/verify 一致性）。
4. **判据宽容度题侧放宽**（S-B：`output_contains_any` / `output_equals_any` 补变体）。
5. **记账**：S-C 工具口径缺口、S-E 骨架偏离各记入对应批次报告一行；S-D realism 项按批次顺手修或留档。
6. **定档**：BLOCKER/裁决清完后按题翻 `status: reviewed`。注意 lint 规则：author 为 `llm:` 时 reviewer 必须 `human:` 前缀（规格书 §5 写的 `llm:<id>-b<n>` 会让全部题违规——此坑 2026-09-22 扩量轮已实测过）。

---

## 附录 A：审阅方法与未覆盖项

- **分工**：13 个家族组由并行审阅代理完成（每个数值断言要求 python 从 fixture 实算），code-0005..0012 因代理环境两次超时由主控亲自审阅；BLOCKER 与裁决项的证据由主控逐条二次实算复核（tab-0006/0008 的 join 语义、fs-0008 的 expect 形状、cfg-0013 的 contains 集、nt-0011 的词表、web 摘要层校准）。
- **X-010 验证方式**：36 个 .py fixture 在完整包布局下 `runpy.run_path` 实跑（`python3 -I` + sys.path 注入），全部退出码 0。
- **未覆盖**：
  - 双 API 跑分闸门（§6）不在本次范围（27B 端点 502 未恢复期间 B2–B5 的 REF 闸门本来就未跑完）；本报告只覆盖题目静态质量面。
  - web fixture 与 `web/recordings/` 真实响应的改写程度未逐条比对（只判结构可信度）。
  - `web_hitcheck` 5/5 由扩量轮已跑过、本次抽查确认 Five alternative phrasings 恰 5 条且含 query_match 词面，未整批重跑。
  - 判分口径（scorer/harness）本身按 §1.2 不在本轮改动范围，S-C/S-D-3 类问题均记录待议。

*报告生成：2026-09-22，人工审阅轮（扩量 40→152）。*
