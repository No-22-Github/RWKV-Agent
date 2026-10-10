## Traps
- 只数类别为电梯的行，水电、门禁等不算。

## Reference solution
1. Read 物业/报修单.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 分析/电梯报修.md with the 6 lines below (first line is the head the prompt dictates).
   # 电梯报修分布
   - 3 号楼: 11 起
   - 5 号楼: 9 起
   - 4 号楼: 7 起
   - 1 号楼: 4 起
   - 2 号楼: 1 起
3. Read 分析/电梯报修.md back to confirm.
Final answer, one sentence: 已把汇总写到 分析/电梯报修.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
