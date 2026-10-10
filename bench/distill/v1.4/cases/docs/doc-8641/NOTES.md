## Traps
- no show is a different outcome and is not listed.

## Reference solution
1. Read docks/appointments.csv (and README.md if needed) to see the columns; filter / group exactly as the prompt says.
2. write_file reports/delayed.md with the 15 lines below (first line is the head the prompt dictates).
   # Delayed appointments
   - AP5002 Northway D1
   - AP5003 Tidecargo D4
   - AP5006 Northway D4
   - AP5007 Northway D3
   - AP5011 Brightline D2
   - AP5012 Oakmoor D1
   - AP5013 Oakmoor D3
   - AP5018 Tidecargo D2
   - AP5028 Brightline D4
   - AP5029 Tidecargo D3
   - AP5031 Oakmoor D2
   - AP5036 Oakmoor D4
   - AP5042 Brightline D4
   Total: 13
3. Read reports/delayed.md back to confirm.
Final answer, one sentence: Wrote the summary to reports/delayed.md (15 lines). Criteria: the new file equals the expected text exactly; the answer names the file and is at most 200 characters (the content is not repeated in the reply).

## Changelog
- v2：S5：终答上限 200→300（老师交代写了哪个文件、按什么口径时常超 200）。

## Why the answer is unique
The prompt fixes the first line, the line format and the order; group totals are all distinct, so the order has no ties.
