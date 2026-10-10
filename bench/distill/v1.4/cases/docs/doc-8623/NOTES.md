## Traps
- 按课程而非教练汇总。

## Reference solution
1. Read 健身房/团课出勤.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 报表/团课出勤.md with the 6 lines below (first line is the head the prompt dictates).
   # 9 月团课出勤
   - HIIT: 265 人次
   - 动感单车: 239 人次
   - 燃脂搏击: 237 人次
   - 瑜伽: 206 人次
   - 普拉提: 106 人次
3. Read 报表/团课出勤.md back to confirm.
Final answer, one sentence: 已把汇总写到 报表/团课出勤.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
