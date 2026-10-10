## Traps
- None. One log, one row per collection, and the cracked_eggs column is a plain count.

## Reference solution
1. List the workspace: the June coop log and a readme.
2. Read coop_log_2026-06.csv and count the rows with cracked_eggs = 0: 19.

## Why the answer is unique
Each collection appears once and the readme confirms one row per collection, so the count of rows
whose cracked_eggs is exactly 0 is fixed. There is no second column that could be mistaken for
the crack count. The answer is 19.
