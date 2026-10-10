## Traps
- 极值按单条记录，不是按日或按方阵求和。

## Reference solution
1. Read 电站/日发电量.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 报告/发电量极值.md with the 3 lines below (first line is the head the prompt dictates).
   # 发电量极值
   最高: 2026-09-17 A 区 4407 千瓦时
   最低: 2026-09-11 B 区 888 千瓦时
3. Read 报告/发电量极值.md back to confirm.
Final answer, one sentence: 已把汇总写到 报告/发电量极值.md，共 3 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
