## Traps
- TR-SIGN: every amount in ledger_2026-08.csv is written as a positive figure and only the entry_type column
  separates charges from credits. Adding the amount column as it stands gives 18141.0, which counts the credits as
  charges rather than as reductions.

## Reference solution
1. List the workspace: the August ledger and a short readme.
2. Read README.md: amounts are entered positive and a credit reduces what an account owes.
3. Read ledger_2026-08.csv, add the charge rows and add the credit rows separately.
4. Charges 17078.6 less credits 1062.4 is 16016.2 pounds owed.

## Why the answer is unique
The readme fixes the meaning of the two entry types, and every row carries exactly one of them, so each amount
either adds to or reduces the month's balance. Since the credits are stored as positive figures, a plain sum of
the column treats a reduction as a charge and gives 18141.0; netting the credits out, as the readme directs, gives
16016.2 pounds.
