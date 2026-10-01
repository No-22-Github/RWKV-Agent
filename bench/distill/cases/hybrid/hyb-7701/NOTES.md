## Traps
- TR-DUPROW: exports/pull-orders-2026-09.csv repeats PO-4025 (2026-09-14, cafe, 11 crates)
  as two identical rows. Counting cafe rows gives 8; counting distinct cafe orders gives 7.
  The README states the export retried and repeats are identical rows.

## Reference solution
1. list_files: the workspace holds exports/, docs/ and README.md.
2. read_file README.md: the export retried, so orders can appear on several identical rows.
3. read_file exports/pull-orders-2026-09.csv. Turn 1: distinct cafe orders PO-4011, 4018, 4021, 4025, 4031, 4038, 4044 = 7. Turns 2 and 3 read off the same rows: the 14-20 September week holds PO-4025 and PO-4031 = 2 orders, 11 + 6 = 17 crates.

## Why the answer is unique
Counting rows instead of orders gives 8, but the README says one row per order with identical repeats, so the repeated row is the same order written twice and cannot be a second order. Every other order appears exactly once, and the weekly window 14-20 September contains exactly two cafe orders either way, so 7, then 2, then 17 are the only readings.

## Five alternative phrasings of the task
1. brindle crane cafe orders september 2026 count
2. how many cafe pull orders went out in september
3. cafe orders in the week of 14 september
4. crates shipped to cafes in the 14-20 september week
5. september pull orders by channel and week
