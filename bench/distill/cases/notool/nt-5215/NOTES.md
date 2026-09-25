## Traps
- TR-AMBIG: the first message asks what the label run costs without saying how many labels the run holds. The band table covers 1000 to 60000 labels in four bands and nothing in the workspace gives the run size, so a first turn that quotes 26.40, 22.10, 18.75 or 15.20 per thousand, or any total built on one of them, has guessed; the correct first turn is a question with no tool call. The second turn gives 14000 labels and the answer is 262.50. The careless answer is 309.40, which applies the mid-band price to the same run.

## Reference solution
1. Turn 1: ask how many labels the run holds; no calls.
2. Turn 2 (14000 labels given): read pricing/label-bands-2026-09.csv, take the Long band that covers 14000 labels, 18.75 per thousand, and multiply by 14. That is 262.50, a total of 2 calls.

## Why the answer is unique
14000 labels falls in exactly one band, the Long band from 10000 to 24999, and the README says a band price applies to the whole run, so 18.75 per thousand times 14 is the only charge. The decoy 309.40 comes from the Mid band, which stops at 9999 labels and cannot cover a 14000-label run. Nothing here states the Hedgerow run size.
