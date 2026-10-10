## Traps
- 评定为「重播」的是另一类，不列入。

## Reference solution
1. Read 苗圃/出苗检查.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file 补苗/出苗偏低.md with the 8 lines below (first line is the head the prompt dictates).
   # 出苗偏低的苗盘
   - MP96 辣椒 85%
   - MP106 西葫芦 80%
   - MP116 番茄 61%
   - MP123 辣椒 63%
   - MP126 番茄 96%
   - MP128 番茄 91%
   共 6 盘
3. Read 补苗/出苗偏低.md back to confirm.
Final answer, one sentence: 已把汇总写到 补苗/出苗偏低.md，共 8 行。 Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
