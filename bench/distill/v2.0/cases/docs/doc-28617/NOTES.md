## Traps
- 件数列不是单数；只数状态为返洗的行。

## Reference solution
1. Read 工单/洗衣工单.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 统计/返洗.md with the 5 lines below (first line is the head the prompt dictates).
   # 返洗统计
   - 丁香路店: 9 单
   - 码头店: 6 单
   - 老街店: 5 单
   - 大学城店: 1 单
3. Read 统计/返洗.md back to confirm.
Final answer, one sentence: 已把汇总写到 统计/返洗.md，共 5 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
