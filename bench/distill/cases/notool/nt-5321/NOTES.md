## Traps
- TR-AMBIG: the first message asks for four days of machine hire without saying which machine is booked. The rate card carries both machines (the twelve metre boom at 148.00 a day, the sixteen metre at 196.50) and nothing in the workspace says which one was booked, so a first turn that quotes either figure has guessed; the correct first turn is a question with no tool call. The second turn names the sixteen metre machine and the answer is four days at 196.50: 786.00. The careless answer is 592.00, four days on the twelve metre rate.

## Reference solution
1. Turn 1: ask which machine is booked, since the hire follows the machine; no calls.
2. Turn 2 (sixteen metre machine named): read rates/machine-rates-2026-09.csv and take the 196.50 daily rate on the sixteen metre row. Four days give 786.00, a total of 2 calls.

## Why the answer is unique
Once the machine is named one row of the card is left: the sixteen metre boom at 196.50 a day, and four days come to 786.00. The decoy 592.00 is four days on the twelve metre machine, so it cannot answer a hire of the sixteen metre one. Nothing in the workspace says which machine the customer booked, so the choice belongs to the requester and no reading of the files settles it before the second turn.
