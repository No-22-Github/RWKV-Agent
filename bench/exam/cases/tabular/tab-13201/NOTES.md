## Traps
No trap; this is an edit-the-previous-product case. Turn 1 writes summary.csv (department,total). Turn 2 depends on it: re-sort descending and add a share column. A model that only appends a column keeps first-appearance order (Quality first) and fails.
Turn 1 is not judged on its own (the file is only checked after the last turn).

## Reference solution
1. Read expenses.csv (or aggregate with a tool) and write summary.csv.
2. Rewrite summary.csv sorted by total descending with the share column.

Final file:
```
department,total,share
Logistics,881.35,38.4%
Packaging,865.65,37.7%
Quality,547.90,23.9%
```
Totals: Logistics 881.35, Packaging 865.65, Quality 547.90; grand total 2294.90.

## Why the answer is unique
Turn 2 fixes the order (biggest first), the column name (share), the unit (%, one decimal). Shares are 38.4% / 37.7% / 23.9% (none sits on a rounding tie). The check is a contains over the whole block, so a missing final newline is fine.

EXAM-CANARY-e82fd28c
