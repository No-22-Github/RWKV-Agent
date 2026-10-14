## Traps
- Answer: Eastern Crane.
- Data volume: 7 data files, 81 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat ops/flights/*.csv | awk -F, '$5=="delayed" && $4>120 {print $2}' | sort | uniq -c | sort -rn | head -3` -> Eastern Crane
Final answer: Eastern Crane.

## Why the answer is unique
airline and status are exact fields; SkyLark Express is a different airline.
