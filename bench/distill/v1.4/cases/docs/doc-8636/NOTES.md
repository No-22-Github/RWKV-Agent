## Traps
- 仪器列是干扰列。

## Reference solution
1. Read 气象/雨量.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 巡检/累计雨量.md with the 6 lines below (first line is the head the prompt dictates).
   # 9 月累计雨量
   - 渡口站: 669 毫米
   - 北岭站: 480 毫米
   - 梨村站: 338 毫米
   - 东滩站: 336 毫米
   - 青石站: 329 毫米
3. Read 巡检/累计雨量.md back to confirm.
Final answer, one sentence: 已把汇总写到 巡检/累计雨量.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
