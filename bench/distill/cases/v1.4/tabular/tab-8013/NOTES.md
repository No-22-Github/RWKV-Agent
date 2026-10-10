## Traps
- TR-NUMFMT: elapsed mixes "940ms" and "1.6s". data_query cannot average these strings (it errors on non-numeric values), and stripping the suffixes without converting gives 357.23.

## Reference solution
1. data_query on jobs/export-runs.csv selecting elapsed (34 rows), or one read_file.
2. Convert ms values to seconds and sum with the calculator, then divide by 34: 1.79 s.
3. (A failed data_query avg with the "not numeric" error is an acceptable first step.)
Final answer, 1-2 sentences: average 1.79 seconds over 34 runs, after converting the millisecond entries to seconds. Criteria: contains 1.79; calculator used; at most one read_file.

## Why the answer is unique
Every value has an explicit unit; converting to seconds and averaging the 34 runs gives one number.
