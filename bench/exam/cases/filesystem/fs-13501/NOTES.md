## Traps
- TR-NEARNAME: 用户写 `Reports/Q3_summary.md`，实际是 `reports/q3-summary.md`（目录大小写、下划线/连字符）。直接读会报不存在；放弃或猜成 q2 会得到 UNKNOWN / 3905.2。
## Reference solution
1. read_file Reports/Q3_summary.md 失败（1）
2. list_files reports 看到 q3-summary.md（2）
3. read_file reports/q3-summary.md，营收 4218.5 万元（3）。ref_calls=3。
## Why the answer is unique
目录里只有一个第三季度文件；q2-summary.md 是第二季度（营收 3905.2），不是 Q3 的相近候选。营收 4218.5，净利润 530.8 是另一项。回答须提到实际读的是 q3-summary（output_contains_any），因为文件名与用户所写不同，如实说明是恢复的一部分。

EXAM-CANARY-a3f10c52
