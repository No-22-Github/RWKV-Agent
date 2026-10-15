# G6 出错恢复补题报告（Sonnet，2026-10-15）

题目目录：`bench/exam/pilots/sonnet-20261015/g6/cases/<scenario>/<id>/`，共 10 题（英 6 / 中 4），作者 `llm:claude-sonnet-5-5`，全部 draft。号段 13501–13510。未提交 git、未改代码和旧题、未做 M4。

## harness 核实（只读）

`internal/agent/eval/webfixture.go`：web_fixture 条目的 `content` 写成 404 页面时，web_fetch 返回成功但正文是「Not Found」；条目带 `error` 字段时，web_fetch 才真的失败（ok:false，带错误文本）。两种都实现了 TR-FETCHFAIL。本批 web-13505、web-13507 用 404 正文，web-13506 用 `error`。另：App harness 的系统提示写明 bash 沙箱「no network, python or node」，所以脚本题里模型本来就知道跑不了 python。

## 题目清单

| ID | 语言 | task_type | 难度 | 题意 |
|---|---|---|---|---|
| fs-13501 | 中 | find_file | L1 | 「打开 Reports/Q3_summary.md 看营收」，实际 reports/q3-summary.md，答 4218.5 |
| cfg-13502 | 英 | read_effective | L1 | config/Settings.yml 实为 config/settings.yaml，答端口 8472 |
| log-13503 | 中 | count_events | L2 | logs/App_error.log 实为 app-error.log，数 9 月 12 日 timeout 错误 15 次（全日期合计 27 为干扰） |
| tab-13504 | 英 | aggregate | L1 | data/Sales-2026.CSV 实为 sales_2026.csv，amount 求和 13113.63 |
| web-13505 | 英 | lookup_value | L1 | 第一条链接 404 正文，第二条写 request_timeout 45s |
| web-13506 | 英 | lookup_value | L1 | 第一条 fetch 报错（error 字段），第二条写免费版单文件 25 MB |
| web-13507 | 中 | lookup_value | L1 | 第一条 404 正文，第二条写 max_retries 5 |
| scr-13508 | 英 | reproduce_output | L1 | net_revenue.py 跑不了（沙箱无 python），复算它打印的净营收 10617.46（不看规则直接累加 gross 为 17154.45） |
| scr-13509 | 英 | reproduce_output | L1 | peak_hour.py 复算最忙小时的成功请求数 24（不排除 5xx 时为干扰值 33） |
| scr-13510 | 中 | reproduce_output | L1 | avg_wait.py 复算平均等待 91.6 分钟（HH:MM 换算、跳过未关闭和 test 行） |

分布与规格书一致：路径不对 4 / 链接失效 3 / 脚本跑不了 3；英 6 中 4。路径不对的四题都用「大小写 + 下划线/连字符/扩展名」双重差异，避免 macOS 大小写不敏感文件系统让直接读取意外成功；回答须提到实际文件名（`output_contains_any`），因为说明实际读了哪个是恢复的一部分。所有非目标文件加 `unchanged`。

## 本地检查

- `bank lint`：10 checked，0 violation。
- `bank verify`：7 ok、3 FAIL，3 个都是 `sabotage_undetected` 探针边界，答案比对本身通过：log-13503（探针改了日志里不影响当天 timeout 计数的数字）、scr-13509（同理，改的是不影响成功请求峰值的数字）、tab-13504（探针删的是用作干扰项的 sales_2025.csv 首行，该文件本来就不参与答案）。没有为过探针加无关断言。
- 负向测试：隔离副本里把 cfg-13502 的 expected_number 改成 8473，verify 报 FAIL。

## 盲解（DeepSeek，App harness，并发 6）

- r1（10 题）：7/10。
- r2（只重跑改过题面的 web-13505、web-13507）：2/2。合并后有效 9/10。r1 中二者的失败原因在下表。

| 题 | r1 结果 | 归类 |
|---|---|---|
| tab-13504 | 失败：awk 默认输出得 13113.60，正确 13113.63 | DeepSeek 真不会（没核对精度），NOTES 已写 Teacher result；题保留 |
| web-13505 / web-13507 | 失败：题面里写了「项目里没写过这个值」，模型只搜工作区，从不调 web_search | 题有问题（题面诱导只查本地）。已修；改成「帮我查一下 / 它的文档在网上」后 r2 通过。「想按文档里写的来」试过，仍不上网，无效 |

「题有问题」已清零。通过题抽读：fs/cfg/log/tab 都在回答里说明了实际文件名；三道脚本题都读脚本后用 awk 复算，并说明没有 python；web-13506 两次 fetch 后给出 25 MB；web-13505/13507 r2 引用了第二条页面。均不是蒙对。

输出目录：`local/runs/exam-gapfill-sonnet-20261015/g6-deepseek-r1`、`g6-deepseek-r2`（`g6-deepseek-r2-failed-prompt` 是第一次修题面但无效的那次）。

## 去污染

v1 / v1.3 / v1.4 / v1.41 / v2.0 全部 0 flagged；v1.42 本地无 cases 目录，未执行。

## 其它发现

- 不让模型上网的倾向：空工作区的 web 题，题面只要出现「本地没有 / 项目里没写」这类话，DeepSeek 就不搜网页；已在 web-13505/13507 的 NOTES 记录。同类题面以后慎用。
- fixture 的 `error` 字段（真失败）与 404 正文两种写法都有用，建议考卷里两种都保留。
