## Traps
- TR-AMBIG: the first message asks for the hire on a thirty-six metre run of hoarding without saying how long the board stands. The card carries a weekly rate for each run length (86.00 for twenty-four metres, 124.50 for thirty-six) and nothing in the workspace says how long the board stays up, so a first turn that quotes a figure has guessed; the correct first turn is a question with no tool call. The second turn says it stands for nine weeks and the answer is nine weeks at 124.50: 1120.50. The careless answer is 774.00, nine weeks at the twenty-four metre rate.

## Reference solution
1. Turn 1: ask how long the board stands, since the hire is charged by the week; no calls.
2. Turn 2 (nine weeks named): read pricing/hoarding-2026-09.csv and take the 124.50 weekly rate on the thirty-six metre row. Nine weeks give 1120.50, a total of 2 calls.

## Why the answer is unique
Once the standing time is named only one multiplication is left: the thirty-six metre run at 124.50 a week for nine weeks is 1120.50. The decoy 774.00 uses the twenty-four metre rate, which the card keys to a shorter run, so it cannot answer a thirty-six metre run. Nothing in the workspace says how long the hoarding stands, so the choice belongs to the requester and no reading of the files settles it before the second turn.
