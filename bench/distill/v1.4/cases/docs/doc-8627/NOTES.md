## Traps
- 船号列是干扰列。

## Reference solution
1. Read 渔港/卸货单.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 报告/卸货量.md with the 6 lines below (first line is the head the prompt dictates).
   # 9 月卸货量
   - 鲳鱼: 8157 公斤
   - 带鱼: 8148 公斤
   - 梭子蟹: 6152 公斤
   - 墨鱼: 5228 公斤
   - 黄鱼: 4236 公斤
3. Read 报告/卸货量.md back to confirm.
Final answer, one sentence: 已把汇总写到 报告/卸货量.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
