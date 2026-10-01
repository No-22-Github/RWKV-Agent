## Traps
- None declared. The scoring run adds a second monthly export the model never saw (expect.run.hidden_files, kept inside receipts/), so a script that hardcodes September's rows or reads only one file misses the October day lines and fails the run check.

## Reference solution
1. 读 till.py：说明文字已把版式定死。
2. 读 receipts/2026-09.csv，确认流水列。
3. 写 till.py：扫 receipts/*.csv，跳过表头，按日期聚合笔数与金额分，按日期排序输出，末行合计。

## Why the answer is unique
合并两份流水（跑分时会再放入 receipts/2026-10.csv）后，小票正好是 2026-09-01,23,19800 / 2026-09-04,6,3300 / 2026-09-08,11,9900 / 2026-09-15,16,11600 / 2026-09-22,8,7200 / 2026-09-28,7,3850 / 2026-10-09,15,13000 / 2026-10-16,6,3000 / 合计,92,71650。版式由 till.py 的说明文字定死；只读 9 月一份文件或把行写死，都会漏掉 10 月的两天，和期望输出对不上。
