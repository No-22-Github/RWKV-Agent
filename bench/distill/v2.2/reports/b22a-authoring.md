# b22a 出题报告（v2.2，题号 34001–34090，共 90 题）

主题：本地查过、确实没有之后，下一步就上网（含对照组：答案就在本地，不该上网）。生成脚本 `bench/distill/tools/b22a/`（`build.py` 无随机数，重跑逐字节一致）。目录 work-v3，判据里没有 read_lines。

## 构成（分子类）
| 子类 | 题数 | 中文 | 多轮 | 题面均长（首轮字数） | web / hyb | 难度 |
|---|---:|---:|---:|---:|---:|---|
| A1 本地搜空 -> 上网 | 40 | 24 (60%) | 20 (50%) | 38.3 | 21 / 19 | L1 23、L2 17 |
| A2 题面说本地没有 | 25 | 13 (52%) | 10 (40%) | 69.6 | 17 / 8 | L1 25 |
| A0 对照：本地有答案 | 25 | 13 (52%) | 11 (44%) | 46.5 | 12 / 13 | L1 25 |
| 合计 | 90 | 50 (56%) | 41 (46%) | — | 50 / 40 | L0 为 0 |

- tool_policy：全部 `must_offer: [list_files, search_text, read_file, web_search, web_fetch]`（陷阱工具必须在目录里才测得出"提供了也不该用/不该跳过"）。
- task_type：web 场景 lookup_value / latest_version / deprecation / error_meaning；hyb 场景 local_first。每题一个独立题族 `b22a-<子类>-<题号>`，品牌、网址、文件名、数值各不相同（A0 的品牌也与 A1 的不重复）。
- 多轮写法：A1 有"第一轮本地问题（禁上网）、第二轮外部问题"的倒序题 3 道，其余是外部事实的追问；A0 多轮是第二轮追问官网现值（此时要求 web_search）。
- A2 题面比 A1/A0 长约 25–30 字，因为要说明"本地没有"；A0 与 A1 的长度、语言、多轮比例接近（A0 46.5 vs A1 38.3）。A2 的说法有变化："我这边没存……""文件夹里肯定没有""没写过任何笔记""None of … is on my machine"，不是都写"本地没有"。

## 判据设计
- A1：`required_tools=[web_search]`；案级 `max_calls {search_text:2, list_files:2}`（倒序多轮题放宽到 3）；`output_contains` 放只在网页里的值，数字/ASCII 值开 `output_contains_token`，中文数量带单位的一律取裸数字（"12 元"取 `12`，避免"12元"与"12 元"之争，Han 邻字算边界）；日期题用 `output_contains_any` 收 16 种写法；约一半题的值只在网页正文、不在摘要里，逼模型 fetch。有 inc 的首轮另加 `output_contains_any` 来源词表（网页/官网/页面/根据/查/来自/according/source/site/from…，大小写都收），要求终答带出处。
- A2：`required_tools=[web_search]`；`forbidden_tools=[list_files, search_text, read_file]`（每轮）；含值判据。
- A0：`forbidden_tools=[web_search, web_fetch]`；`output_contains` 为文件里的值；`output_excludes` 放网页上那个不同的值（含有/无空格两种写法）。追问官网现值的第二轮不再禁网并要求 web_search。
- hitcheck：90 题 NOTES 的五种说法全部命中 fixture（query_match 取品牌首词，如 `Quartzline` 而不是 `Quartzline API`，防止模型搜短名搜不到）。
- 离线自测：对 131 个轮次，用标准答案判过、用三种"没找到/工作区里没有/建议去官网看"的答案判不过（0 例误过）。

## 自检结果
- build.py 连跑两次，90 题全部文件逐字节一致。
- `gate.sh v2.2 '*-340[0-9][0-9]'`：`90 case(s) checked, 0 violation(s)`，`verify 90 / 90`。
- `corpus loadcheck --cases bench/distill/v2.2/cases`：`loadcheck: 355 case(s) load`（含其他批次）。

## 每个子类的"走错方向"答法（判据如何判它不过）
- A1-1：本地 search_text 换三五个关键词反复搜，最后答"工作区里没有相关信息"。无 web_search -> required_tools 不过；`search_text` 超过 2 次 -> max_calls 不过；也不含网页独有的值。
- A1-2：本地没搜到就凭记忆报一个版本/价格（编造）。值不在 fixture 里 -> output_contains 不过；没调 web_search 同样不过。
- A2-1：题面已说本地没有，仍先 list_files / search_text 看一眼。forbidden_tools 命中即不过。
- A2-2：不碰本地、也不上网，直接回答"我无法联网/不清楚"。required_tools 缺 web_search，且没有网页独有的值。
- A0-1：答案明明在 CHANGELOG/记录文件里，却去 web_search 拿官网最新值。forbidden_tools 命中；终答里出现的网页值被 output_excludes 拦住。
- A0-2：不查文件就说"本地没有，建议看官网"。缺 output_contains 的本地值；第二轮才允许上网的题里，第一轮用网页值也不过。

## 已知风险 / 老师最可能答错的题
- A1 的来源词表很宽但仍可能卡住只报一个数、不写出处的老师答卷（如 34001 只回"5.2.1"）；这类通常是可接受的答案，若老师通过率偏低，可去掉来源词表。
- 34004 / 34035（弃用日期）：页面里有两个日期（只读 vs 停服；SMS 弃用日），判据只收停服日期写法，答"只读日期"会判错，属于有意设计。
- 34021（月白租房）：判据靠"不再/免费/不收"类词，写法偏窄，可能漏收同义说法。
- 多轮倒序题（34017、34023、34037）：第一轮禁上网、第二轮要上网，老师若第一轮就上网会整题失败，这是想要的行为区分。
- A0 多轮题（如 34066、34068、34076）：第二轮"官网上现在写多少"要求 web_search，老师可能因第一轮已本地作答而在第二轮不查网，直接复述前文。
- 价格类裸数字（"4""8""9"）靠 token 边界判，纯凭数字撞中的概率低但非零。
- 倒序题的 max_calls 放宽到 3，其余 A1 为 2；若老师习惯 list_files + search_text + read_file 的完整三连，read_file 不受限，但 list_files/search_text 各超 2 次会被判错。
- 去污染：所有品牌、网址均为虚构的 `.example` 域，题面没有对照任何测试集。

## 去污染返修（主 Agent 验收后）
去污染标记 11 题，原因都是 fixture 文件名过于通用（README.md、todo.md、notes.txt、plan.md 等）与测试集撞名，题面相似度 ≤ 0.16。返修只换文件名，题面、判据、答案、网页 fixture 不变：
- 与 exam 撞名：web-34001、34006、34020、34027、34042、34047、34062；与 bashprobe/reserve 撞名：hyb-34058、web-34010、web-34052、web-34056。
- 改法：换成带业务含义的名字，如 `看板说明-销售部.md`、`commute/monthly-pass-plan.md`、`logs/tallowmere-upstream-2026-09-16.log`、`build-cleanup-checklist.md`、`vendor-callback-reminder.txt`、`scratch/sdk-eval-greeting.txt`。这 11 题的题面都没有点名文件，所以只有 fixture 键和 NOTES/verify.py 随脚本重新生成。
- 返修后：build.py 两次逐字节一致；`gate.sh` 为 0 violation、verify 90/90；`loadcheck` 通过；八个测试目录（exam、workbank、p13、bashprobe 的 cases / cases-b14 / reserve、weatherprobe 的 cases / reserve）去污染均为 `90 candidates … 0 flagged`。
