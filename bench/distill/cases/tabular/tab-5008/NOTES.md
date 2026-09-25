## Traps
- TR-DUPROW: six records in service_log_2026-08.csv appear twice because the export ran twice. Counting lines
  gives 50 instead of 44.

## Reference solution
1. List the workspace: the depot's service log and a short readme.
2. Read README.md: one record per bicycle, and the export was run twice.
3. Read service_log_2026-08.csv and count the distinct bike_id values: 44.

## Why the answer is unique
The readme states one record per bicycle, and every reprinted line is identical to its original down to the
record_id and the service date, so the repeats describe the same visit and not a second one. Counting distinct
bicycle identifiers therefore gives 44; counting lines gives the inflated 50.
