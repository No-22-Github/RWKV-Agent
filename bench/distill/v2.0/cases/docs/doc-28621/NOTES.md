## Traps
- 「待取」还没超期，不计。

## Reference solution
1. Read 驿站/滞留件.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 清理/超期滞留.md with the 6 lines below (first line is the head the prompt dictates).
   # 超期滞留件
   - C 架: 7 件
   - D 架: 6 件
   - B 架: 5 件
   - A 架: 2 件
   - 大件区: 1 件
3. Read 清理/超期滞留.md back to confirm.
Final answer, one sentence: 已把汇总写到 清理/超期滞留.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
