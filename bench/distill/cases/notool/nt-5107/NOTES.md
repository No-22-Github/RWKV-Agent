## Traps
- TR-AMBIG: the first message asks what the seal kit costs per unit without naming a currency, and every row carries a euro and a pound fee, so a first turn that reports 148.50 or 127.30 has guessed. The correct first turn is a question with no tool call. The second turn names the euro column and the answer is 148.50. The careless answer is the pound figure 127.30.

## Reference solution
1. Turn 1: ask which currency the quote should be in; no calls.
2. Turn 2 (euros named): read supplier/quotes-2026-09.csv and take fee_eur for SEAL-40. That is 148.50, a total of 2 calls.

## Why the answer is unique
The clarified request names the euro column, and SEAL-40 has exactly one euro fee, 148.50. The decoy 127.30 is the pound fee on the same row: the README says quotes arrive in both currencies and that the accounts team pays the one the invoice is raised in, so a euro invoice cannot be settled at the pound figure. The other rows are different parts.
