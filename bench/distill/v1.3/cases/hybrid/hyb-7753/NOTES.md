## Traps
- TR-AMBIG: the author appears in three quarters while a statement is per quarter; summing all her rows gives 890.18, which is no single statement's payout.

## Reference solution
1. Turn 1: the statement's quarter is a required parameter the user must name; ask which quarter (no tool calls).
2. Turn 2: the user picks Q2 2026.
3. Read royalties/royalties.csv, keep Nadia Kowalczyk Q2 rows: 236.68 (The Salt Marshes) and 84.96 (Nine Elms).
4. Total 321.64 and reply with the number alone.

## Why the answer is unique
 The decoy 890.18 spans Q1, Q2 and Q3; the clarified request is one statement, and statements are paid per quarter per the README, so only the two Q2 rows count and the total is 321.64. Turn 1 is judged only on asking for the quarter.

## Five alternative phrasings of the task
1. How much is due to Nadia Kowalczyk this statement?
2. Work out Nadia Kowalczyk's royalty payout.
3. What does Nadia Kowalczyk get paid on her statement?
4. Give me the payout figure for Nadia Kowalczyk.
5. Total Nadia Kowalczyk's royalties for her statement.
