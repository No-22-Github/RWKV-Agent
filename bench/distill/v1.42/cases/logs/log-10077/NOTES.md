## Traps
- Answer: 325. TR-DECOY: grep -w host=redis-1, which also matches redis-1-replica (a hyphen is not a word character) gives 681.
- TR-MULTISRC: 6 files; the first one alone gives 50.
- Data volume: 6 data files, 100 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat logs/cache/*.log | awk '$2=="host=redis-1" && !/failover/' | wc -l` -> 325
Final answer: 325 lines from redis-1 that are not failovers.

## Why the answer is unique
The README defines the match; one pattern gives one count.
