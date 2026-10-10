## Traps
- 4 分本身合格，只数小于 4 的。

## Reference solution
1. Read 民宿/卫生评分.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 反馈/低分房型.md with the 5 lines below (first line is the head the prompt dictates).
   # 低分房型
   - 大床房: 13 次
   - 双床房: 12 次
   - 亲子房: 9 次
   - 榻榻米房: 7 次
3. Read 反馈/低分房型.md back to confirm.
Final answer, one sentence: 已把汇总写到 反馈/低分房型.md，共 5 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
