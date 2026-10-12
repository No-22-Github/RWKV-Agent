## Traps
- TR-DECOY: exact answer 1600; the loose reading (prefix match on route and status) gives 4941.
- TR-MULTISRC: 4 files; the first file alone gives 435.

## Reference solution
Turn 1: bash: `cat ferry/*.txt | awk -F'\t' '$2=="R7" && $3=="boarded" {s+=$4} END{print s}'` -> 1600
Final answer: 1600 seats.

## Why the answer is unique
route and status are whole-value columns. The README (ferry/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Total boarded seats for route R7 over the four days?
2. Add up seats where route is R7 and status is boarded.
3. Per ferry/README.md, how many seats boarded on R7?
4. Sum the seats column for R7 rows with status boarded.
5. What is the combined number of boarded seats on R7?
