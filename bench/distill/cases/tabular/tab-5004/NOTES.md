## Traps
- None. The category and the month both sit in a single column of a single file, and the log holds no repeats.

## Reference solution
1. List the workspace: one lending log and a short readme.
2. Read loans.csv and keep the rows with category garden and a loan_date in March 2026: L-5502, L-5503, L-5504, L-5505, L-5507 = 5.

## Why the answer is unique
The question fixes both the category and the month, and each of the five matching rows is a distinct loan id, so
nothing is counted twice and nothing qualifies that is not listed. The February garden loan and the April garden
loans fall outside March, so 5 is the only count.
