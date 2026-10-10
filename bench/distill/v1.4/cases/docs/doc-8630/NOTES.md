## Traps
- 班次列是干扰列。

## Reference solution
1. Read 印刷厂/废品登记.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 月报/废品张数.md with the 5 lines below (first line is the head the prompt dictates).
   # 9 月废品张数
   - 小森 3 号: 4357 张
   - 海德堡 2 号: 3129 张
   - 高宝 4 号: 2616 张
   - 海德堡 1 号: 2360 张
3. Read 月报/废品张数.md back to confirm.
Final answer, one sentence: 已把汇总写到 月报/废品张数.md，共 5 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
