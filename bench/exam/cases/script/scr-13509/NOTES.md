## Traps
- 沙箱无 python，脚本跑不起来，需读脚本后用 awk/sort/uniq 复算。
- TR-DECOY: 脚本只统计状态码 < 500 的请求；不排除 5xx 时最忙小时的数是 33。
## Reference solution
1. read_file scripts/peak_hour.py（1）
2. bash 按小时分组、排除 5xx、取最大（2–3）= 24（小时 14）。ref_calls=3。
## Why the answer is unique
成功请求（状态码 <500）按 UTC 小时计数，最大值 24，次大值与之不同，无并列。

EXAM-CANARY-0f6c83d2
