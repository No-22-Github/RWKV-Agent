## Traps
- 沙箱无 python，需读脚本后用 awk 复算（时间为 HH:MM，要换算成分钟）。
- TR-DECOY: 脚本跳过未关闭的工单和 priority=test 的行；若只跳过未关闭的，平均为 82.9。
## Reference solution
1. read_file scripts/avg_wait.py（1）
2. bash/awk 复算（2–3）= 91.6。ref_calls=3。
## Why the answer is unique
有效行 15 条，等待分钟之和除以条数，保留一位小数得 91.6。

EXAM-CANARY-b7d3e1c8
