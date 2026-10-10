## Traps
- TR-SIGN: every amount is stored as a positive figure and the direction lives in the DR/CR
  column. A reader who adds every amount as money in, treating debits as credits, lands on 2151.42
  instead of the true closing balance 4674.18.

## Reference solution
1. List the workspace: the August statement and a readme.
2. Read README.md: DR is money out, CR is money in, amounts are positives.
3. Read statement_2026-08.csv and walk the rows from the opening balance, adding CR and taking
   away DR: 4674.18.

## Why the answer is unique
The readme assigns the direction to the DR/CR column and states that amounts carry no sign of
their own, so the only balance the statement supports is credits less debits from the opening
row. The decoy 2151.42 adds the debits in, which is the opposite of what DR means there. The answer
is 4674.18.
