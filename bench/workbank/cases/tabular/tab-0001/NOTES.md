## Traps
- None. L0 baseline: one plain CSV, no formatting on numbers, no missing
  values, no duplicate rows, no total row, no sign ambiguity.

## Reference solution
1. list_files - find orders_june.csv in the workspace (1)
2. read_file orders_june.csv - 12 rows, every order_date in June 2026 (2)
3. calculator - sum of line_total = 5548.95 (3)

## Why the answer is unique
There is exactly one data file; every row belongs to June 2026, and
line_total is a plain decimal column with no formatted cells, gaps or
repeats. The README fixes the meaning of line_total (per-order charge
including tax), so the sum has a single reading.

<!-- WORKBANK-CANARY-7c1d44a2 : this file must never enter training corpora -->
