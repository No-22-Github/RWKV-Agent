# G4 长输入补题报告（Sonnet 批 g4）

18 题（中文 9 / 英文 9），题目在 `bench/exam/pilots/sonnet-20261015/g4/cases/<scenario>/<id>/`，每题含 case.json、verify.py、NOTES.md、gen.py（固定种子生成 fixture）。共用生成工具 `g4/_lib.py`、`g4/_doc.py`。全部 draft、作者 llm:claude-sonnet-5-5，未提交 git。

## 题目清单（全部 L2：TR-LONG + 一个干扰陷阱）

| ID | 语言 | task_type | fixture | 题意 |
|---|---|---|---|---|
| log-13301 | 中 | locate_error | 121 KB | 网关日志里 req-7f3a2c 经过哪几个服务（有 req-7f3a2d 近似 ID 干扰，链路 6 行都在 64KB 之后） |
| log-13302 | 英 | root_cause | 117 KB | 网关统一报 502，真正出错的后端服务是谁（答 ledger-svc） |
| log-13303 | 中 | time_window | 129 KB | 早上 5 点那一小时 ERROR 最多的是哪一分钟（05:37；01:12 是全局峰，05:08 是 WARN 峰） |
| log-13304 | 英 | count_events | 125 KB | 配置重载标记行之后 worker-b3 的 lease expired 错误数（10；全文 30，前 64KB 内 17） |
| log-13305 | 中 | locate_error | 119 KB | 部署完成标记之后第一条 ERROR 的错误码（E7302；标记前 4 行有 E4417 干扰） |
| log-13306 | 英 | aggregate_jsonl | 156 KB | JSONL 访问日志里 export 接口被 429 的不同用户数（22；按行数是 52） |
| tab-13307 | 中 | aggregate | 144 KB | 3000 行订单 CSV，9 月退款成功金额合计（7904.77；含退款失败是 13023.86） |
| tab-13308 | 英 | filter_count | 185 KB | 1800 行 JSONL，8 月礼品卡、加拿大、已发货订单数（25） |
| tab-13309 | 中 | filter_count | 105 KB | 2400 行工单，9 月 P1 已关闭且超过 48 小时的张数（30；含恰好 48 小时是 35） |
| tab-13310 | 英 | rank | 162 KB | 3600 行流水，Q3 退货最多的门店（Eastgate Mall；全文排名第一是 Harbor Point） |
| tab-13311 | 中 | aggregate | 185 KB | 3000 行销售明细，华东 8 月销售额（数量×单价，不含赠品，46401.40） |
| tab-13312 | 英 | aggregate | 119 KB | 1 个骑手 9 月已完成线路公里数合计（1973.9） |
| doc-13313 | 中 | policy_lookup | 49 KB | 差旅手册：上海住宿每晚上限（2025 表 650，后面的 2026-07 公告 780） |
| doc-13314 | 英 | policy_lookup | 54 KB | 数据手册：应用日志保留天数（旧 90，后面的修订通知 45） |
| doc-13315 | 中 | policy_lookup | 50 KB | 售后规定：拆封电子产品无理由退货天数（旧 3，修订 10） |
| doc-13316 | 英 | policy_lookup | 55 KB | 内部手册：SDK 4.2 默认超时（3.x 表 30 秒，4.x 小节 12 秒） |
| doc-13317 | 中 | policy_lookup | 50 KB | 员工手册：司龄 6 年的年假天数（2024 表 8，2026 修订 11） |
| doc-13318 | 英 | policy_lookup | 54 KB | 采购手册：组长单笔审批上限（2025 年 500，修订 900） |

分布对照规格 2.5：日志 6、大表 6、长文档 6；每子类中英各半；总计中 9 / 英 9。

## 规格与实际的冲突（需要主 Agent 决定）

- 规格写文档 30～60 KB，又要求答案不在前 64 KB。两者矛盾：60 KB 的文件整个都在 read_file 的 64 KB 之内。我按文档大小范围做（49～55 KB），把新版本小节放在 43～48 KB 处（断言 >= 40 KB），旧版本在 15～18 KB 处。日志和表满足“前 64KB 无答案”，gen.py 里有断言（日志：目标行偏移 >= 65536；表：前 64KB 内没有目标月份数据，或前缀算出的结果与答案不同）。如果要文档也逼出分页读取，需要把文档放宽到 70 KB 以上。
- 为让 sabotage 探针可靠，每个 verify.py 开头加了 fixture 的 sha256 完整性断言（改动 fixture 即失败）。这是因为探针会把 fixture 里“恰好等于答案的数字”加 1，而对聚合题那个数字只是时间戳/毫秒里碰巧相同的字符，答案并不会变（log-13304、log-13306 首次报 sabotage_undetected）。verify.py 仍然独立重新计算答案。

## M1

- lint：18 checked，0 violation。
- verify：18 passed，0 failed，探针全部 detected（没有“答案来自用户消息”类误报）。
- 负向测试：隔离副本把 tab-13309 的 expected_number 改成 31，verify 报 verify_expect_mismatch，FAIL。

## M2 盲解（DeepSeek，App harness，并发 6）

- r1（`local/runs/exam-gapfill-sonnet-20261015/g4-deepseek-r1`）：账面 17/18。
  - doc-13318 失败：老师搜 “Team lead” 只看到 2025 表就答 500（真不会，NOTES 已写 Teacher result）。
  - doc-13317 账面通过但其实答错（答 8）：题面里的“11 月”碰巧等于正确答案 11，`expected_number_in_text` 把它当作命中。这是题有问题（答案数字与题面日期撞车），已修：题面改成“2020 年 3 月入职，六年出头”。r2（`g4-deepseek-r2`，只重跑这一题）通过，回答明确引用 2026 修订表。
- 剔除假通过后：r1 实际 16/18，修题后合计 17/18（94%）。“题有问题”已清零。
- 抽读通过题：日志、表题均用 bash 管道计算（3～4 步），回答带出过滤条件，不是蒙的；doc-13313 同时提到 650 和 780 但结论是 780（因此未对旧值使用 output_excludes）。
- 注意：DeepSeek 在 4～13 秒内完成，说明沙箱 bash 让大表聚合很容易；对 RWKV 才是难点。

## M3 去污染

v1 759 / v1.3 782 / v1.4 1012 / v1.41 430 / v2.0 940 候选，全部 0 flagged；v1.42 本地没有 cases 目录，未执行。日志 `local/runs/exam-gapfill-sonnet-20261015/g4-decontam.txt`。

## 其他发现

- scorer 边界：`expected_number_in_text` 会被题面里出现的同值数字触发（上面 doc-13317）。出数字题时要检查答案是否在题面里出现，最好在 gen.py 里加断言。
- 中文表的“前 64KB 行数”要按字节算（汉字 3 字节），我在 `_lib.prefix_lines` 里统一处理；用字符切片会算错。
- 未改旧题、internal/、cmd/，没有跑 M4，没有 git 操作。
