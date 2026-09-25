## Traps
- TR-ABSENT: the log holds the 2026 season only, so there is no August 2025 figure to compare with. A reader who
  reports the August 2026 weight instead answers 1049.5, which is not the change the request asks for.

## Reference solution
1. List the workspace: the picking log and a short readme.
2. Read README.md: the weighing station was installed in May 2026, so the log begins that month.
3. Read picking_log_2026.csv: every row is from the 2026 season and no row carries an August 2025 weight.
4. The change against August 2025 cannot be computed, so the answer is UNKNOWN.

## Why the answer is unique
A percentage change needs both the earlier and the later figure. The readme states when the log starts and the
file holds only 2026 rows, so the earlier figure is absent from the workspace rather than equal to zero: nothing
says the 2025 harvest was nil. Reporting the August 2026 weight, or treating the change as 0, would both assert
something the files do not show, so the only answer the workspace supports is UNKNOWN.
