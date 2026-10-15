# Sonnet 补题：g3en 批（G3 英文追问与改需求）报告

## 结论
12 题全部完成，目录 `bench/exam/pilots/sonnet-20261015/g3en/cases/<scenario>/<id>/`，编号 13201～13212，全英文，每题 2 条用户消息、每轮都有 expect。lint 0 违规，verify 12/12 通过。DeepSeek 盲解第一轮 8/12，其中 2 题是我的判分写得不好（已修，单独重跑 2/2 通过），2 题是 DeepSeek 真的不守"记忆轮不调工具"。"题有问题"类已清零。作者 `llm:claude-sonnet-5-5`，全部 draft，未提交 git。

## 题目清单
| ID | 子类 | task_type | 难度 | 题意 |
|---|---|---|---|---|
| tab-13201 | 改需求 | write_summary | L0 | 先按部门汇总报销写 summary.csv，再要求按金额从高到低并加占比列（终态判文件） |
| cfg-13202 | 改需求 | edit_value | L0 | prod workers 4 改 6，再让 staging 取 prod 现值的一半（=3） |
| doc-13203 | 改需求 | write_structured | L1 | 纪要行动项写 todo.md，再把截止日期挪到括号里并删掉已完成项 |
| log-13204 | 纠正 | count_events | L0 | 昨天哪个服务 5xx 最多（billing），纠正为前天（search） |
| cfg-13205 | 纠正 | read_effective | L1 | prod 端口 8443，纠正为问 staging（9443） |
| tab-13206 | 纠正 | filter_count | L0 | Denver 8 月销量 887，纠正为 Austin（1073） |
| log-13207 | 追问 | root_cause | L1 | 发布 2026.09.3 哪步失败（migrate），追问在哪台主机（db-03） |
| doc-13208 | 追问 | policy_lookup | L1 | 国内每日餐补 55，追问 4 天合计 220（旧值 45 是干扰） |
| code-13209 | 追问 | find_callers | L1 | apply_discount 定义在哪，追问谁在用（cart.py、promo_report.py；legacy 版本是干扰） |
| cfg-13210 | 记忆 | read_effective | L1 | 查 prod 连接池大小 24，第 2 轮不调工具复述并算三倍 72 |
| log-13211 | 记忆 | locate_error | L1 | 夜间备份最近一次成功时间（9/15 02:14，9/16 那条是失败），第 2 轮不调工具复述 |
| doc-13212 | 记忆 | policy_lookup | L1 | 开封软件退货期 14 天，第 2 轮不调工具算 9 月 1 日购买的最后退货日（9 月 15 日） |

分布与要求一致：改需求 3 / 纠正 3 / 追问 3 / 记忆 3，各场景分散（tab 2、cfg 3、doc 3、log 3、code 1）。题面都是随手聊天口吻，没有工具名和格式模板，结尾没有重复套话。记忆轮用 `tools: []` + `require_active_no_call`。

## 本地检查
- `bank lint`：12 checked，0 violation。
- `bank verify`：12/12 通过。破坏探针一开始有 6 题报"改了首行答案不变"，不是"答案来自用户消息"那种，所以我修了题而不是放过：日志题改成最新在前、verify 里断言"陷阱前提还在"（如最新一行是失败、存在后续的 smoke WARN）；文档题让首行就是 Dana 的行动项；代码题 verify 要求调用者必须既 import 又调用；cfg-13205 的 verify 校验第 1 轮 prod 端口也是从夹具算出的；log-13204 加了"第一名不得并列"断言。这些断言在 verify.py 里，case.json 没加无关判分。
- 负向测试：隔离副本里把 tab-13206 第 2 轮 expected_number 1073 改成 1074，verify 报 FAIL。

## 盲解（DeepSeek，app harness，并发 6）
| 轮次 | 成绩 | 说明 |
|---|---|---|
| r1 | 8/12 | 失败：cfg-13205、log-13204、cfg-13210、doc-13212 |
| r2 | 2/2（只重跑改过的 cfg-13205、log-13204） | 合计等效 10/12 |

失败归类：
- cfg-13205、log-13204：**题有问题（已修）**。回答是对的（9443 / search），但表格或列表里顺带写了旧答案（8443 / billing 的计数），触发规格要求的 `output_excludes`。把 excludes 换成 `output_first_line_contains_any`（结论必须出现在首行），仍能抓"重复旧答案当结论"。tab-13206 用的排除数字 887 没被误伤，保留。
- cfg-13210、doc-13212：**DeepSeek 真不会**。记忆轮明明说了"不用再看了"，它还是又调了工具（doc-13212 还把年份写成 2025，不判）。已在 NOTES 加 Teacher result。
- 通过的题抽读了 log-13207、log-13211、doc-13208、code-13209，答案是真的从证据来的，不是蒙对。

## 去污染
v1 / v1.3 / v1.4 / v1.41 / v2.0 全部 0 flagged；v1.42 本地没有 cases 目录，未执行。

## 发现 / 需要决定
1. 规格要求的纠正题 `output_excludes` 旧答案，在好回答里常被误伤；建议规格改为"首行含新答案"这种写法（`output_first_line_contains_any`）。
2. 题级 `expect.files` 只在末轮后检查，3 道改需求题的第 1 轮只能写 `expect: {}`（NOTES 已说明）；doc-13203 的 contains 无法拒绝块外多出来的行。
3. 记忆轮的成败主要看模型会不会克制调工具，DeepSeek 在这 3 题里 2 题没守住，可作为 RWKV 的区分度参考。

输出目录：`local/runs/exam-gapfill-sonnet-20261015/g3en-deepseek-r1`、`g3en-deepseek-r2`。
