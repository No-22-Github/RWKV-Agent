## Traps
- Answer: 33. TR-DECOY: counting failed DELETEs too gives 48.
- TR-MULTISRC: 6 files; the first one alone gives 6.
- Data volume: 6 data files, 154 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat logs/edge/*.log | awk '$6=="\"DELETE" && $7=="/api/v2/cart" && ($9==200 || $9==201)' | wc -l` -> 33
Final answer: 33 successful DELETEs on /api/v2/cart.

## Why the answer is unique
Status and path are exact fields of each line; the README pins the endpoint, so one count results.
