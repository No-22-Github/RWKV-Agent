## Traps
- TR-DECOY: inbox/orders.csv 里另一单 SO-77388（云雾绿茶）与来信订单同表相邻，粗读容易张冠李戴。 A careless pass reports `云雾绿茶`.

## Reference solution
1. List inbox/ and read the letter.
2. Read inbox/orders.csv and pull the row matching the order in the letter.
3. Read policies/damage-flow.md and check the 72-hour window against the dates, then answer.

## Why the answer is unique
The letter names SO-77342, and that is the only order the claim can be checked against; SO-77388 is a different order for 云雾绿茶 that the letter never mentions. The claim landed one day after the 2026-09-03 signature, inside the 72-hour window, so the policy reading is unique.
