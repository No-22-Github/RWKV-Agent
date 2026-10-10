## Traps
- 汇总.md 不带日期，不参与比较。

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：最新的是 2026-09-20 那份（报表/站点-20260920.csv）。
判据见 case.json（contains=[] any=['20260920', '2026-09-20', '9 月 20 日', '9月20日', '9 月 20 号', '9月20号'] excl=[]）。

## Why the answer is unique
四份周报里最大的日期是 20260920。
