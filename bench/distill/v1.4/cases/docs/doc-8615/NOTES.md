## Traps
- 「待复查」不是「异常」，不能计入。

## Reference solution
1. Read 巡检/蜂场检查.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 报告/9月蜂场异常.md with the 6 lines below (first line is the head the prompt dictates).
   # 9 月蜂场异常巡检
   - 杏花坡: 6 次
   - 老松岭: 4 次
   - 南坝: 3 次
   - 石桥头: 2 次
   - 河湾: 1 次
3. Read 报告/9月蜂场异常.md back to confirm.
Final answer, one sentence: 已把汇总写到 报告/9月蜂场异常.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
