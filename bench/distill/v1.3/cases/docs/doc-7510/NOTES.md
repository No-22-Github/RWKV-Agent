## Traps
- TR-DECOY: hr/pto-balances.csv 里 Priya Raman 的余额正好等于上限，粗看 2/2 容易当成超限。 A careless pass reports `Priya Raman`.

## Reference solution
1. Read hr/pto-balances.csv and compare each days_left with its carryover_cap.
2. Read hr/pto-policy.md for the January 31 cutoff and the staff-band option.
3. Name the employees over cap and the options for their excess days.

## Why the answer is unique
Priya Raman has 2 days against a cap of 2, so her balance carries over in full and only Nadia Kovac (9 vs 5) and Tomas Lindqvist (14 vs 8) exceed their caps. The policy sets January 31 as the cutoff and grants the training-budget conversion to the staff band alone, so the options are pinned.
