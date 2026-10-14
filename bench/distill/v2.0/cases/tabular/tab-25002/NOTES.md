## Traps
- None. The answer is the sum of one column of the only data file, and every row is recorded once.

## Reference solution
1. List the workspace: one harvest log and a short readme.
2. Read hive_harvest.csv and add the honey_kg column: 9.4 + 12.7 + 21.3 + 8.9 + 15.2 + 7.6 + 26.4 + 11.8 + 4.3 + 18.5 + 13.9 + 10.7 = 160.7.

## Why the answer is unique
The readme states one row per hive extraction, so no row stands for two harvests, and the question asks for
the whole season. The file holds a single harvest per hive and every value in honey_kg is a net weight in
kilograms, so the season total can only be 160.7.
