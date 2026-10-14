## Traps
- 已撤销的单不计入。

## Reference solution
1. Read 停车/违停单.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 月报/违停统计.md with the 6 lines below (first line is the head the prompt dictates).
   # 违停单统计
   - 访客区: 19 张
   - 地库一层: 15 张
   - 地库二层: 14 张
   - 西门: 11 张
   - 东门: 7 张
3. Read 月报/违停统计.md back to confirm.
Final answer, one sentence: 已把汇总写到 月报/违停统计.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
