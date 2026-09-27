## Traps
- TR-DECOY: six Birchcop rows re-run from the March spot-check sit in the file with higher counts
  than a typical April run. A reader who totals each depot across the whole file hands the shield
  to Birchcop with 440; the April figures alone give Dringhouses 367.

## Reference solution
1. List the workspace: the dispatch file and a readme.
2. Read README.md: six rows are March spot-check re-runs carrying March dates.
3. Read depots/parcels_2026-04.csv, keep the April-dated rows, total parcels per depot, and take
   the highest: 367.

## Why the answer is unique
The readme dates the spot-check re-runs to March, and their dispatch_date says March on every
row, so they cannot be April volume. Totalling April only gives one figure per depot with
Dringhouses leading; the 440 that folds March re-runs into April is the decoy. The answer is 367.
