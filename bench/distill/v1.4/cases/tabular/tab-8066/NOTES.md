## Traps
- 无。

## Reference solution
1. 读表（或 data_query）分别求 9/1–9/7 与 9/8–9/14 的发电量合计。
2. calculator：(后一周 - 前一周) / 前一周 * 100，precision 1 → 31.7。
终答示例：31.7。判据：expected_number 31.7，调用过 calculator。

## Why the answer is unique
两周各 7 天，增长率以前一周为基数。
