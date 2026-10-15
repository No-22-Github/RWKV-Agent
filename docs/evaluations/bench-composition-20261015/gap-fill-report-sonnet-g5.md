# G5「查不到时要说明」补题报告（Sonnet，批次 g5）

位置：`bench/exam/pilots/sonnet-20261015/g5/cases/<scenario>/<id>/`，共 16 题（中文 10 / 英文 6），号段 13401–13416，全部 draft、author=llm:claude-sonnet-5-5。

## 题目清单（全部 L1，tag 均为 TR-ABSENT / DEC）

| ID | task_type | 语言 | 题意（用户怎么问） |
|---|---|---|---|
| cfg-13401 | missing_keys | 中 | 生产环境 max_retry_backoff 是多少（只有 retry_backoff_ms=500） |
| cfg-13402 | missing_keys | 中 | 连接池 idle_timeout（只有 max_lifetime_seconds） |
| cfg-13403 | missing_keys | 中 | 订单表 coupon_amount 字段类型（只有 discount_rate） |
| cfg-13404 | missing_keys | 中 | nginx proxy_read_timeout（只有 connect/body 超时） |
| cfg-13405 | missing_keys | 英 | staging 的 audit_retention_days（只有 log_retention_days=14） |
| cfg-13406 | missing_keys | 英 | 生产的 SMTP_TIMEOUT（只有 staging 里有） |
| doc-13407 | policy_lookup | 中 | 成都住宿标准，正文指向缺失的《附录B-住宿标准.xlsx》 |
| doc-13408 | policy_lookup | 中 | 回滚步骤，指向缺失的 rollback-runbook.md |
| doc-13409 | extract_items | 中 | 纸箱单价，指向缺失的《价格表.pdf》 |
| doc-13410 | policy_lookup | 英 | /export 限流，指向缺失的 docs/ratelimits.md |
| doc-13411 | extract_items | 英 | 营销预算，指向缺失的 Q4-budget.xlsx |
| web-13412 | lookup_value | 中 | lumenq 的 queue_ttl_seconds 默认值（页面只有别的选项） |
| web-13413 | lookup_value | 中 | 星桥数据库 3.8 是否支持分区表（只有 3.5/3.6 说明） |
| web-13414 | error_meaning | 中 | kestrel-cli 的 E_SLOT_4017（错误码页无此项） |
| web-13415 | lookup_value | 英 | Quillbird webhook 的 max_body_bytes |
| web-13416 | error_meaning | 英 | Marlin-DB 的 ERR_SNAPSHOT_88 |

分布 6 / 5 / 5，中英 10 / 6，与规格一致。判分：`must_state_unverified` 钉缺失项名字（配置键、文件名、错误码、版本号）+ 表示「没有」的 `output_contains_any`（中文词组、英文照 cfg-0011）；web 题加 `required_tools: [web_search]`；没有任何 `output_excludes`；干扰值只在 `trap_decoys`。「查了哪、缺什么、下一步」写进每题 NOTES 的读回答细则，由人工读轨迹时看，不自动判，也不锁话术。

## 本地检查

- lint：16 checked，0 violation。verify：16 通过，0 失败（verify.py 校验缺失项确实不在 fixture 里，并对每个文件的首行做完整性断言，所以探针删首行会被检出；web 题无文件，探针按规则跳过）。
- 负向测试：隔离副本里给 cfg-13401 的 prod.yaml 追加 `max_retry_backoff: 8000`，verify 报 FAIL。
- 本批无数字题，故负向测试用「补上缺失键」代替改 expected_number。

## DeepSeek 盲解（`local/runs/exam-gapfill-sonnet-20261015/`）

| 轮次 | 范围 | 成绩 |
|---|---|---|
| r1 `g5-deepseek-r1` | 全 16 题 | 11/16（cfg/doc 11/11 全过；web 0/5） |
| r2 `g5-deepseek-r2` | web 5 题（改题面后） | 2/5 |
| r3 `g5-deepseek-r3` | web 5 题（再改题面） | 5/5 |

最终等效：16/16（cfg/doc 取 r1，web 取 r3，两者题面均为最终版）。

失败归类（全部是「题有问题」，已修，现已清零）：
- r1 web 5 道：题面像在问本地代码（「lumenq 里 queue_ttl_seconds 默认值多少」），DeepSeek 只搜了工作区就答「查不到」，没调用 web_search。修法：题面加入「官方文档我们没存本地 / 开源的 / 托管的」等背景。
- r2 另外 3 道（web-13413、13415、13416）：模型仍只查工作区，甚至声称「没有联网能力」。修法：加用户自然会说的「帮我查一下官网 / Can you look up … on their site」。没有放宽任何判分。
- 注意：web 题对「题面是否带出外部来源」很敏感，这一点本身就是模型行为差异（DeepSeek 会误称没有网络），后续测 RWKV 时同样值得关注；这不是 harness 问题。

抽读通过的回答：cfg-13401/13404/13406、doc-13407/13408 都说了查了哪些文件、缺什么、下一步。两点瑕疵（不改判分）：cfg-13404 回答补了「nginx 默认 60 秒」（提示是软件默认值而非这里的配置，可接受）；cfg-13406 回答误称「没有生产 env 文件」（实际有，只是不含该键），但仍点名了缺失项并给了否定表述，判分通过。

## 去污染

v1、v1.3、v1.4、v1.41、v2.0 均为 0 flagged；v1.42/cases 本地不存在，未执行。

## 发现 / 需要主 Agent 决定

- 没有发现旧题或检查器问题；本批无 verify 探针误报。
- 判分只能确认「点名了缺失项 + 含否定词」；「说明查了哪、给下一步」没有自动判据，若要自动化需要新的判分字段（记录，不要求现在做）。
- web 题 fixture 的 query_match 用产品名（小写子串）；若模型搜索词里不含该产品名会搜到空结果，同样是合理的「查不到」，不影响判分。
