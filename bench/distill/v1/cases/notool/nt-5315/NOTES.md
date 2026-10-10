## Traps
- TR-AMBIG: the first message asks for the storage charge on eighty pallets held for a fortnight without saying which month they come in. The card carries two seasons (peak 4.85 per pallet per week, off peak 3.40) and the season follows the intake month, and nothing in the workspace says when Marlbrook Dairy load, so a first turn that quotes either figure has guessed; the correct first turn is a question with no tool call. The second turn names the November intake and the answer is two weeks at the off peak rate: 544.00. The careless answer is the peak figure 776.00.

## Reference solution
1. Turn 1: ask which month the consignment comes in, since the season and the rate follow it; no calls.
2. Turn 2 (November named): read rates/storage-card-2026.csv and take the off peak rate of 3.40 per pallet per week. Eighty pallets for two weeks is 160 pallet weeks, so 160 x 3.40 = 544.00, a total of 2 calls.

## Why the answer is unique
Once the intake month is named the season is fixed: November falls in the October to May band, so the off peak rate of 3.40 applies and 160 pallet weeks give 544.00. The decoy 776.00 is the same fortnight at the peak rate, which the card reserves for June to September, so it cannot answer a November intake. Nothing in the workspace says when the consignment arrives, so the choice belongs to the requester and no reading of the files settles it before the second turn.
