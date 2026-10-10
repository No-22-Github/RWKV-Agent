## Traps
- TR-AMBIG: the first request names the Cranmere account, and the ledger carries two
  accounts of that name, Stackwell and Winster. Winster's outstanding balance is 580.00
  ((980.00 - 400.00) + (1120.00 - 1120.00) + (715.00 - 715.00)); Stackwell's is 1095.50
  ((1240.00 - 1240.00) + (865.50 - 0.00) + (430.00 - 200.00)). The ledger alone cannot
  say which customer the chase is for, so the assistant has to ask.

## Reference solution
1. list_files: the workspace holds accounts/cranmere-2026-09.csv and README.md.
2. read_file accounts/cranmere-2026-09.csv: two accounts trade as Cranmere, so the
   request is not yet settled and the assistant asks which one is meant.
3. Turn 2 fixes the Winster account. Subtract each row's paid amount and add:
   (980.00 - 400.00) + (1120.00 - 1120.00) + (715.00 - 715.00) = 580.00 + 0.00 + 0.00
   = 580.00.

## Why the answer is unique
After the clarification one account is in scope. Each row states what was invoiced and
what has been paid against it, so the amount outstanding on an account is the sum of the
differences. Winster's three rows give 580.00; the decoy 1095.50 is Stackwell's balance,
a real figure for the other customer, and the chase was settled on Winster before the
rows were subtracted.

## Five alternative phrasings of the task
1. stackwell supplies cranmere account outstanding balance
2. how much is outstanding on the cranmere account
3. cranmere winster and stackwell balances september
4. stackwell supplies credit account september
5. cranmere invoices paid and outstanding
