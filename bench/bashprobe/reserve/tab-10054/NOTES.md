## Traps
- Turn 1: 131.
- Turn 2: 19.
- Data volume: 7 data files, 80 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat ops/flights/*.csv | awk -F, '$5=="cancelled"' | wc -l` -> 131
Turn 2: bash: `awk -F, '$5=="cancelled"' ops/flights/CTU.csv | wc -l` -> 19
Final answer (last turn): 19 cancellations out of CTU.

## Why the answer is unique
airline and status are exact fields; SkyLark Express is a different airline.
