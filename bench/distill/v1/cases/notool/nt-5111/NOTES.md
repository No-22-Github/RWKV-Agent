## Traps
- TR-AMBIG: the first message asks what Harlow Bay owes, and the aging sheet carries two accounts under that name (Harlow Bay Marine at 7412.30 and Harlow Bay Chandlery at 918.75), so a first turn that reports either figure has guessed. The correct first turn is a question with no tool call. The second turn names the marine account and the answer is 7412.30. The careless answer is the chandlery figure 918.75.

## Reference solution
1. Turn 1: ask which Harlow Bay account is meant; no calls.
2. Turn 2 (Harlow Bay Marine named): read ledger/aging-2026-09.csv and take outstanding_gbp for that account. That is 7412.30, a total of 2 calls.

## Why the answer is unique
The sheet has one row per account and only one is named Harlow Bay Marine, so 7412.30 answers the clarified request on its own. The decoy 918.75 is the chandlery account, which the README and the customer's own reply both treat as a separate customer with its own terms, so the two figures cannot be added or swapped. The other rows are unrelated customers.
