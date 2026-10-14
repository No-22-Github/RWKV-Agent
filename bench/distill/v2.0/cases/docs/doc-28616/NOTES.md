## Traps
- 饲养员列是干扰列，按区域汇总，不是按人。

## Reference solution
1. Read 饲养/投喂记录.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 报告/9月投喂汇总.md with the 6 lines below (first line is the head the prompt dictates).
   # 9 月各区投喂量
   - 猛禽区: 500 公斤
   - 草食区: 361 公斤
   - 两栖馆: 335 公斤
   - 灵长区: 315 公斤
   - 夜行馆: 159 公斤
3. Read 报告/9月投喂汇总.md back to confirm.
Final answer, one sentence: 已把汇总写到 报告/9月投喂汇总.md，共 6 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
