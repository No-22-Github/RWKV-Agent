## Traps
- Answer: 9833.
- TR-MULTISRC: 7 files; the first one alone gives 850.
- Data volume: 7 data files, 77 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat ops/flights/*.csv | awk -F, '$2=="Southern Pearl" && $5=="delayed" {s+=$4} END {print s}'` -> 9833
Final answer: 9833 minutes of delay.

## Why the answer is unique
airline and status are exact fields; SkyLark Express is a different airline.
