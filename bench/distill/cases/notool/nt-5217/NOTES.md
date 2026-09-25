## Traps
- TR-AMBIG: the first message gives the area (forty square metres) but not the finish, and the schedule prices three finishes at 14.60, 22.40 and 31.85 per square metre. Nothing in the workspace says which finish Pennock Fabrications ordered, so a first turn that quotes 584.00, 896.00 or 1274.00 has guessed; the correct first turn is a question with no tool call. The second turn names powder coat and the answer is 896.00. The careless answer is the zinc plate total 584.00.

## Reference solution
1. Turn 1: ask which finish the order carries; no calls.
2. Turn 2 (powder coat named): read coatings/schedule-2026-09.csv, take the 22.40 per square metre of the powder coat row and multiply by 40. That is 896.00, a total of 2 calls.

## Why the answer is unique
With the finish named, one row of the schedule applies, and 22.40 per square metre over forty square metres is 896.00. The decoy 584.00 is the zinc plate rate over the same area, and a different finish has a different price, so it cannot answer an order that specifies powder coat. No file here names a finish for the Pennock order.
