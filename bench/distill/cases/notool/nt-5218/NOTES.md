## Traps
- TR-AMBIG: the first message asks what the Friday cover visit costs without saying which grade of carer takes it, and the rate sheet prices three grades at 17.20, 19.65 and 23.40 an hour. Nothing in the workspace says who is going to Larkwell Road, so a first turn that quotes 137.60, 157.20 or 187.20 has guessed; the correct first turn is a question with no tool call. The second turn names a senior carer for eight hours and the answer is 187.20. The careless answer is the care assistant total 157.20.

## Reference solution
1. Turn 1: ask which grade of carer is taking the visit; no calls.
2. Turn 2 (senior carer, eight hours): read rates/carer-grades-2026-09.csv, take the 23.40 hourly rate of the senior carer row and multiply by 8. That is 187.20, a total of 2 calls.

## Why the answer is unique
The grade names a single row, and eight hours at 23.40 is 187.20. The decoy 157.20 is the care assistant rate over the same eight hours, and the README ties the charge to the grade of the carer who takes the visit, so a rate belonging to another grade cannot answer a senior carer shift. No file here says who covers Larkwell Road.
