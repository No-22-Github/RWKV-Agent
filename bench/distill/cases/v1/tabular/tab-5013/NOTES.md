## Traps
- TR-SIGN: refunds sit in their own column as positive amounts, so a reader who adds the two columns together
  gets 8836.13 instead of the amount actually owed.

## Reference solution
1. List the workspace: the August ledger and a short readme.
2. Read README.md: refunds are positive figures that reduce what the member owes.
3. Read ledger_2026-08.csv, add the charge column and the refund column, and take the charges less the refunds:
   8118.19.

## Why the answer is unique
The readme fixes the direction of both columns: a charge is owed and a refund reduces what is owed, and both are
stored as positive numbers. No other column can be read as a charge or a refund, so the only net figure the file
supports is 8118.19. Adding the two columns instead gives 8836.13.
