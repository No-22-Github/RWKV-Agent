## Traps
- crew is a distractor; group by block.

## Reference solution
1. Read harvest/picks.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file reports/harvest-by-block.md with the 6 lines below (first line is the head the prompt dictates).
   # September harvest by block
   - Hillside: 128 t
   - Lower Terrace: 109 t
   - Creek: 89 t
   - Ridge: 69 t
   - Orchard Row: 38 t
3. Read reports/harvest-by-block.md back to confirm.
Final answer, one sentence: Wrote the summary to reports/harvest-by-block.md (6 lines). Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
