## Traps
- TR-AMBIG: the first message asks for the carriage on twenty-four cylinders without saying whether the customer collects or takes delivery. The carriage sheet carries both terms (depot collection 4.60, yard delivery 9.25) and nothing in the workspace says which term was agreed, so a first turn that quotes either figure has guessed; the correct first turn is a question with no tool call. The second turn says they collect from the depot and the answer is twenty-four cylinders at 4.60: 110.40. The careless answer is 222.00, the same order on the delivery rate.

## Reference solution
1. Turn 1: ask whether the cylinders are collected from the depot or delivered to the yard, since the carriage follows the term; no calls.
2. Turn 2 (depot collection named): read pricing/carriage-2026-09.csv and take the depot collection charge of 4.60 per cylinder. Twenty-four cylinders give 110.40, a total of 2 calls.

## Why the answer is unique
Once the term is named one row of the carriage sheet is left: depot collection at 4.60 per cylinder, and twenty-four of them come to 110.40. The decoy 222.00 is the same order at the yard delivery rate, which the README reserves for customers the run delivers to, so it cannot answer an order the customer collects. Nothing in the workspace says which term Priory Road Allotments agreed, so the choice belongs to the requester and no reading of the files settles it before the second turn.
