## Traps
- 「破损」不是「延误」。

## Reference solution
1. Read 行李/转盘记录.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 运行/行李延误.md with the 5 lines below (first line is the head the prompt dictates).
   # 行李延误
   - 1 号转盘: 7 件
   - 4 号转盘: 6 件
   - 3 号转盘: 5 件
   - 2 号转盘: 4 件
3. Read 运行/行李延误.md back to confirm.
Final answer, one sentence: 已把汇总写到 运行/行李延误.md，共 5 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
