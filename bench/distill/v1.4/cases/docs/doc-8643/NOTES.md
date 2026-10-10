## Traps
- sensor fault is not an excursion.

## Reference solution
1. Read clinic/fridge-log.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file audit/excursions.md with the 5 lines below (first line is the head the prompt dictates).
   # Temperature excursions
   - Fridge C: 7
   - Fridge D: 6
   - Fridge A: 4
   - Fridge B: 2
3. Read audit/excursions.md back to confirm.
Final answer, one sentence: Wrote the summary to audit/excursions.md (5 lines). Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
