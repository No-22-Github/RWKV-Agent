## Traps
- 片名列是干扰列。

## Reference solution
1. Read 影院/售票.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 运营/影厅票数.md with the 6 lines below (first line is the head the prompt dictates).
   # 9 月影厅票数
   - 2 号厅: 1886 张
   - 巨幕厅: 1649 张
   - IMAX 厅: 1580 张
   - 1 号厅: 1510 张
   - 4 号厅: 675 张
3. Read 运营/影厅票数.md back to confirm.
Final answer, one sentence: 已把汇总写到 运营/影厅票数.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
