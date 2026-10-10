## Traps
- TR-AMBIG: the first message asks what a load of soil and rubble costs without giving the weight, and the tariff prices that category in two bands (up to 6 t at 84.00, over 6 t at 142.50), so a first turn that quotes either band has guessed. The correct first turn is a question with no tool call. The second turn gives 8.5 tonnes and the answer is 142.50. The careless answer is the light band 84.00.

## Reference solution
1. Turn 1: ask how heavy the load is; no calls.
2. Turn 2 (8.5 tonnes): read gate-fees/tariff-2026-09.csv and take the soil and rubble row whose band covers the weight. That is 142.50, a total of 2 calls.

## Why the answer is unique
8.5 tonnes sits above the 6 t split, so only the over-6-t band for soil and rubble answers the clarified request, and it is 142.50. The decoy 84.00 is the same category's light band, which stops at 6 t: the README says the band is read off the weight on the weighbridge ticket, and 8.5 t is above that limit, so 84.00 cannot apply. The green waste rows are a different category.
