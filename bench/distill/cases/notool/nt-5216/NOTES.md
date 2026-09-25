## Traps
- TR-AMBIG: the first message asks what the Thursday crossing costs without saying which vehicle goes. The fare sheet has one price per vehicle class (88.00, 164.50, 297.00) and nothing in the workspace says what is going to Portmore, so a first turn that quotes any of the three has guessed; the correct first turn is a question with no tool call. The second turn names the rigid and the answer is 164.50. The careless answer is the van fare 88.00.

## Reference solution
1. Turn 1: ask which vehicle is making the crossing; no calls.
2. Turn 2 (rigid named): read crossings/fares-2026-09.csv and take the fare_gbp of the Rigid row. That is 164.50, a total of 2 calls.

## Why the answer is unique
Each vehicle class has a single row, so once the rigid is named 164.50 is the only fare that answers the clarified request. The decoy 88.00 is the van fare and a van is a different class on the same sheet, so it cannot stand for a rigid crossing. No file here says which vehicle runs to Portmore.
