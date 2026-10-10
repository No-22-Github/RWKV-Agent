## Traps
- TR-NUMFMT: every amount is written like "$1,284.50", so column aggregation over the raw cells
  errors out and the sum must be done by hand. A reader who drops the pence and adds only the
  pound figures gets 37962.0 instead of 37980.85.

## Reference solution
1. List the workspace: the consignment sheet and a readme.
2. Read README.md: one row per lot sold, amounts in pounds.
3. Read consignments_2026-08.csv and total the 41 amounts, keeping the pence: 37980.85.

## Why the answer is unique
Each of the 41 rows carries one sale amount with pence, and the readme confirms one row per lot
sold. Stripping the currency punctuation leaves a single unambiguous number per row, so the only
total the sheet supports is 37980.85; the pound-only figure 37962.0 discards the pence the rows carry.
