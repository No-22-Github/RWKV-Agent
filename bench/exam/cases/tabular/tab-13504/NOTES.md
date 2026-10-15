## Traps
- TR-NEARNAME: 用户写 `data/Sales-2026.CSV`，实际 `data/sales_2026.csv`。放弃会答 UNKNOWN。
## Reference solution
1. read_file data/Sales-2026.CSV 失败（1）
2. list_files data（2）
3. data_query 或 read_file 对 amount 求和 = 13113.63（3）。ref_calls=3。
## Why the answer is unique
sales_2025.csv 是另一年（2 行），与 2026 文件名只差年份，不是被问文件的近名。2026 文件 14 行 amount 之和 13113.63。回答须提到 sales_2026。

## Teacher result
DeepSeek 找到了 sales_2026.csv 并说明了文件名差异，但用 awk 默认输出求和得 13113.60（%.6g 丢了分），与正确的 13113.63 差 0.03，超出 0.01 容差。模型真错（没有核对精度），判分保留。

EXAM-CANARY-c40b6e73
