## Traps
- 情况有两种异常写法，都要算，只排除「平稳」。

## Reference solution
1. Read 养老院/夜巡记录.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 交接/夜巡异常.md with the 5 lines below (first line is the head the prompt dictates).
   # 夜巡异常
   - 一层: 13 次
   - 三层: 7 次
   - 四层: 4 次
   - 二层: 3 次
3. Read 交接/夜巡异常.md back to confirm.
Final answer, one sentence: 已把汇总写到 交接/夜巡异常.md，共 5 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
