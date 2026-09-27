## Traps
- TR-DUPROW: the finance export re-appended three lines, so payments DP-707 and DP-703 appear two
  and three times. Summing every line reports 18437.15 paid; the distinct payment runs total 14528.11.

## Reference solution
1. List the workspace: the awards list, the payments log and a readme.
2. Read README.md: the export re-appended lines during the migration.
3. Read awards/payments.csv, collapse the re-appended identical lines to one payment each, and
   total the amounts: 14528.11.

## Why the answer is unique
Each payment run has one payment_id, and the re-appended lines match a run on every column, so
they are the same payment written twice rather than money leaving the account twice. The decoy
18437.15 counts those re-writes as extra cash; the actual payout is 14528.11.
