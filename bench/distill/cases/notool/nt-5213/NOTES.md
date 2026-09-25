## Traps
- TR-AMBIG: the first message asks for the nightly figure for a new patrol site without saying how many visits a night the site takes. The rate card lists four visit counts (2, 3, 4 and 6) and nothing in the workspace says what Cairnmuir Business Park has asked for, so a first turn that quotes any of 58.00, 74.50, 96.40 or 131.20 has guessed; the correct first turn is a question with no tool call. The second turn says four visits and the answer is 96.40. The careless answer is the three-visit figure 74.50.

## Reference solution
1. Turn 1: ask how many visits a night the site takes; no calls.
2. Turn 2 (four visits named): read patrols/rate-card-2026-09.csv and take the nightly_gbp of the four-visit row. That is 96.40, a total of 2 calls.

## Why the answer is unique
Four visits is a row of its own on the rate card, so 96.40 is the only nightly figure that answers the clarified request. The decoy 74.50 is the three-visit price and belongs to a different contract size, and the README says the price follows the number of visits, so 74.50 is not a reading of a four-visit site. The rate card says nothing about which site takes which count, and no file here names Cairnmuir Business Park at all.
