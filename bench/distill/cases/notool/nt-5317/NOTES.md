## Traps
- TR-AMBIG: the first message asks for the price of four shopfront panels without saying which customer the quote is for. The agreement sheet carries two discounts (standard trade 10 per cent, silver account 17.5 per cent) and nothing in the workspace ties a customer to an agreement, so a first turn that quotes either figure has guessed; the correct first turn is a question with no tool call. The second turn names Netherton Stores on the silver account and the answer is four panels at 145.00 less 17.5 per cent: 478.50. The careless answer is 522.00, the same four panels on standard trade terms.

## Reference solution
1. Turn 1: ask which customer the quote is for, since the trade agreement and the discount follow it; no calls.
2. Turn 2 (Netherton Stores, silver account): read pricing/panels-2026-09.csv for the aluminium shopfront list price of 145.00 and pricing/trade-agreements.csv for the silver account discount of 17.5 per cent. Four panels are 580.00 less 101.50 = 478.50, a total of 2 calls.

## Why the answer is unique
Once the customer is named the agreement follows from what the requester says, and the silver account discount of 17.5 per cent is the only one left: 580.00 less 17.5 per cent is 478.50. The decoy 522.00 applies the standard trade discount of ten per cent to the same four panels, which the README reserves for standard trade customers, so it cannot answer a silver account quote. Nothing in the workspace ties Netherton Stores to an agreement, so the choice belongs to the requester and no reading of the files settles it before the second turn.
