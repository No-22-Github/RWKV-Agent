## Traps
- Answer: 396. TR-DECOY: an unescaped regex (dots match _ and x, .p99 included) gives 1737.
- TR-MULTISRC: 6 files; the first one alone gives 48.
- Data volume: 6 data files, 84 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat metrics/*.txt | awk '$2=="api.v2.latency"' | wc -l` -> 396
Final answer: 396 samples of api.v2.latency.

## Why the answer is unique
The README defines the match; one pattern gives one count.
