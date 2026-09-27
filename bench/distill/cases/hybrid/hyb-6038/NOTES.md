## Traps
- TR-MISSING: the kwh column mixes an empty cell, NA and a dash for the days the meter logged nothing. TW-01 recorded on 11 of the 14 days; dividing its sum across all 14 days gives 703.93 instead of 895.91.

## Reference solution
1. Turn 1: list_files to find the meter export.
2. read README.md: dash, NA and empty cells are days with no reading, and they stay out of averages.
3. read meters/output-2026-06.csv and average TW-01's eleven recorded days: 9855 / 11 = 895.91.
4. Turn 2 needs no further call: the same read holds TW-02's twelve recorded days, 10363 / 12 = 863.58.

## Why the answer is unique
The README defines what an unread day means, so an average can only run over recorded days: 11 for TW-01 and 12 for TW-02. Spreading the sums across all 14 days treats no-reading days as zero output, a reading the file and its notes do not support, and it lands on 703.93 rather than 895.91. Each turbine has exactly 14 rows, so no other denominator or numerator combination is available.

## Five alternative phrasings of the task
1. skelgill head turbine tw-01 june average
2. average daily output tw-02 first fortnight
3. skelgill meter export june kwh
4. wind farm daily average june first half
5. skelgill head turbine yields june 2026
