## Traps
- None. The log has 90 lines; WARN lines about slow upstream are not ERRORs.

## Reference solution
1. Search "ERROR" in logs/pay-api-2026-09-15.log: 7 matches, first 2026-09-15T14:02:44Z, last 2026-09-15T14:16:30Z.
2. write_file incidents/2026-09-15-pay-api.md with the three lines `start: 2026-09-15T14:02:44Z`, `end: 2026-09-15T14:16:30Z`, `errors: 7`.
3. Read the new file back.
Final answer, one sentence: wrote incidents/2026-09-15-pay-api.md (errors ran from 2026-09-15T14:02:44Z to 2026-09-15T14:16:30Z, 7 in total). Criteria: the file contains the three lines; the answer names the file.

## Why the answer is unique
ERROR lines are marked by level; timestamps are copied verbatim, so the three lines are fixed.
