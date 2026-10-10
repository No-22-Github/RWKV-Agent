## Traps
- single rows, not per-target sums.

## Reference solution
1. Read observatory/sessions.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file notes/session-extremes.md with the 3 lines below (first line is the head the prompt dictates).
   # Session extremes
   Longest: OB78 M31 339 min
   Shortest: OB72 M13 29 min
3. Read notes/session-extremes.md back to confirm.
Final answer, one sentence: Wrote the summary to notes/session-extremes.md (3 lines). Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
