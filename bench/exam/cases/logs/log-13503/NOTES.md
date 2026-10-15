## Traps
- TR-NEARNAME: 用户写 `logs/App_error.log`，实际 `logs/app-error.log`（大小写、下划线/连字符）。
- TR-DECOY: 日志含 9-11、9-13 两天，也含非 timeout 的 ERROR；全部日期 timeout 数为 27，不是答案。
## Reference solution
1. read_file logs/App_error.log 失败（1）
2. list_files logs（2）
3. search_text 或 read_file 统计 9 月 12 日 ERROR 且含 timeout 的行，共 15（3）。ref_calls=3，但有两个陷阱按 L2 记。
## Why the answer is unique
只数 2026-09-12 当天、级别为 ERROR、消息含 timeout 的行：15。INFO/WARN 行不含 timeout 字样；其他日期的 timeout（合计 27）错误答案。access.log 与 error.log 名字不近。

EXAM-CANARY-5d27e0b9
