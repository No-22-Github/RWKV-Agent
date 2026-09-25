## Traps
- TR-HEADER: kiln_drying_log_2026.csv ends with a `TOTAL` line holding the column sums for the whole season.
  That line carries 17352.9 kilograms of dried weight, which is the figure for all three months rather than for June,
  so a reader who takes the log's own total answers 17352.9 instead of 6243.1.

## Reference solution
1. List the workspace: the seasonal drying log and a short readme.
2. Read kiln_drying_log_2026.csv and keep the rows whose dry_month is 2026-06; the last line is a `TOTAL` line
   with no month and is not a batch.
3. Add the dry_kg of the 22 June batches: 6243.1 kilograms.

## Why the answer is unique
The readme says one row per drying batch and gives dry_kg as the weight off the kiln floor, so each June row
carries the weight that batch contributed. The `TOTAL` line names no grower or variety and repeats the sum of all
sixty rows, so it describes the season rather than a batch and cannot stand for the June figure. Adding the June
rows gives 6243.1.
