## Traps
- TR-DECOY: crate_log_2026-06.csv sits beside the July log and sorts first, so counting the wrong month gives
  40.
- TR-HEADER: the last line of the July log is a `TOTAL` line, which adds one to any count that treats it as a
  delivery and gives 51.

## Reference solution
1. List the workspace: two monthly crate logs and a short readme.
2. Read README.md: one log per month and one row per delivery.
3. Read crate_log_2026-07.csv, step past the `TOTAL` line and count the delivery rows: 50.

## Why the answer is unique
The request fixes the month as July 2026, and only crate_log_2026-07.csv carries July dates, so the June log holds
a different month's deliveries and cannot contribute to the count. Inside the July log the `TOTAL` line records
the month's turnover rather than a delivery. The 50 rows that name a date and a supplier are the deliveries, so
the count is 50.
