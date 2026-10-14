## Traps
- Answer: 32. TR-DECOY: counting SkyLark Express gives 63.
- TR-MULTISRC: 7 files; the first one alone gives 0.
- Data volume: 7 data files, 80 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat ops/flights/*.csv | awk -F, '$2=="SkyLark" && $5=="cancelled"' | wc -l` -> 32
Final answer: 32 SkyLark departures were cancelled (SkyLark Express not included).

## Why the answer is unique
airline and status are exact fields; SkyLark Express is a different airline.
