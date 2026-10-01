## Traps
- 无陷阱（L0）。要点：答案是一段 2–5 句的中文自然语言解释，必须落在配置的真实取值上：每天 01:15 归档一次，归档保留 retention_days 14 天，压缩用 zstd，notify_webhook 为空（不发通知），dry_run 关闭（真实执行）。只说「定时归档配置」而不给具体值的答案过不了判据。

## Reference solution
1. 读 archive-policy.json（1 次调用）。
2. 终答（中文，自然语言 3–5 句）：归档任务每天 01:15 跑一次；归档结果保留 14 天（retention_days）；打包压缩用 zstd；notify_webhook 为 null 说明归档完成不对外发通知；dry_run 为 false 说明不是演练、会真实归档。

## Why the answer is unique
五个键的取值彼此独立且无歧义，没有第二份规则文件，也不存在优先级覆盖问题。判据的必含事实（01:15、zstd、retention_days）只能来自读完这份配置；「每天凌晨归档」这类不含具体取值的答法、或把 14 天说成别的数的解释都过不了。
