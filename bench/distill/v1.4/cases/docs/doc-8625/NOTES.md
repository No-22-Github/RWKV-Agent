## Traps
- 阀门列是干扰列。

## Reference solution
1. Read 农场/灌溉记录.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 报告/灌溉用水.md with the 6 lines below (first line is the head the prompt dictates).
   # 9 月灌溉用水
   - 北坡茶园: 937 立方
   - 温室一号: 660 立方
   - 东坡梨园: 498 立方
   - 河滩玉米: 391 立方
   - 南洼菜地: 327 立方
3. Read 报告/灌溉用水.md back to confirm.
Final answer, one sentence: 已把汇总写到 报告/灌溉用水.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
