## Traps
- TR-DUPROW: five runs were written out a second time, so the file holds 70 data lines for 65 runs.
- TR-HEADER: the file ends with a `TOTAL` line that names no line or grade and carries the month's coil count,
  which brings a plain line count to 71.

## Reference solution
1. List the workspace: the June braiding log and a short readme.
2. Read README.md: one row per run, the last line is the month's coil total, and the export ran twice.
3. Read braiding_log_2026-06.csv and count one run per distinct run_id, ignoring the `TOTAL` line: 65 runs.

## Why the answer is unique
The readme defines both wrinkles: the `TOTAL` line carries the coil count rather than a run, and the second export
repeated five runs under their original run_id and every other field unchanged. Counting distinct run_id values
over the real rows leaves 65 runs, and no reading of the file turns a reprinted line or the `TOTAL` line into a
run of its own.
