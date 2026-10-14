## Traps
- 「取消」不是「晚点」。

## Reference solution
1. Read 校车/到站记录.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 家校/校车晚点.md with the 6 lines below (first line is the head the prompt dictates).
   # 校车晚点
   - 4 路: 8 次
   - 5 路: 6 次
   - 3 路: 3 次
   - 1 路: 2 次
   - 2 路: 1 次
3. Read 家校/校车晚点.md back to confirm.
Final answer, one sentence: 已把汇总写到 家校/校车晚点.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
