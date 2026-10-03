## Traps
- None.

## Reference solution
1. Read docs/kpi-targets.md: Q3 and Q4 rows are lines 7 and 8.
2. replace_lines start_line 7, end_line 8 with the two rows `| Q3 | 2 | 30 | 91 |` and `| Q4 | 2 | 28 | 92 |`.
3. Read the file back.
Final answer, one sentence: Q3 and Q4 rows in docs/kpi-targets.md now carry the new targets (2/30/91 and 2/28/92). Criteria: exact file content; output mentions Q3.

## Why the answer is unique
The prompt gives every new value; the table format is fixed, so the resulting file is unique.
