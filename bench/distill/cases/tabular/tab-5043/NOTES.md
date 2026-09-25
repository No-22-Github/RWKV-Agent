## Traps
- TR-HEADER: run_log_2026.csv ends with a `TOTAL` line holding the finished area for the whole season. That line carries 2164.7 square metres, which is the area of all three months, so a reader who takes the log's own total answers 2164.7 instead of 741.7.

## Reference solution
1. List the workspace: the seasonal run log and a short readme.
2. Read run_log_2026.csv and keep the rows whose run_month is 2026-06; the last line is a `TOTAL` line with no month and is not a run.
3. Add the area_m2 of the 22 June runs: 741.7 square metres.

## Why the answer is unique
The readme says one row per slab run and gives area_m2 as the finished area of that run, so each June row carries the area that run produced. The `TOTAL` line names no machine or date, and its figure is the sum of all sixty-six rows, so it describes the season rather than a run and cannot stand for the June area. The June rows add up to 741.7 square metres.
