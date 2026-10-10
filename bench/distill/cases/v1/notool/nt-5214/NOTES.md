## Traps
- TR-AMBIG: the first message asks what a bin collection costs without saying how heavy the load is. The price list is written by band (up to 1000, 2500, 4000 and 8000 kg) and nothing in the workspace gives the weight of the Longmoor Depot load, so a first turn that quotes 146.00, 232.50, 318.75 or 452.00 has guessed; the correct first turn is a question with no tool call. The second turn gives 3200 kg and the answer is 318.75. The careless answer is the 2.5-tonne band figure 232.50.

## Reference solution
1. Turn 1: ask how heavy the load is; no calls.
2. Turn 2 (3200 kg given): read collections/band-prices-2026-09.csv and take the first band whose up_to_kg covers 3200 kg, the Heavy row at 318.75. That is 318.75, a total of 2 calls.

## Why the answer is unique
The bands are written so that each weight falls in exactly one of them, and 3200 kg is over 2500 and within 4000, so 318.75 is the only band that covers it. The decoy 232.50 is the 2.5-tonne band and would leave 700 kg unbilled, which the README rules out by making the band the first one that covers the load. No file here records a weight for Longmoor Depot.
