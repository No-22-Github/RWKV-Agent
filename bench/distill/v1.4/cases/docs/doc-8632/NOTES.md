## Traps
- 取单条记录的极值，不是按闸口或按日求和。

## Reference solution
1. Read 景区/闸机客流.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 报告/客流极值.md with the 3 lines below (first line is the head the prompt dictates).
   # 客流极值
   最忙: 2026-09-08 北门 5777 人次
   最闲: 2026-09-16 北门 138 人次
3. Read 报告/客流极值.md back to confirm.
Final answer, one sentence: 已把汇总写到 报告/客流极值.md，共 3 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
