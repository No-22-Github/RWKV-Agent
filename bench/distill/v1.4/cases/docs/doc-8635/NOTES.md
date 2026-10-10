## Traps
- 没有过滤条件，不要只数「待件」或某个部件。

## Reference solution
1. Read 网咖/机位报修.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 维护/机位报修.md with the 5 lines below (first line is the head the prompt dictates).
   # 9 月机位报修
   - 包间: 20 单
   - VIP 区: 19 单
   - 竞技区: 17 单
   - 散座区: 14 单
3. Read 维护/机位报修.md back to confirm.
Final answer, one sentence: 已把汇总写到 维护/机位报修.md，共 5 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
