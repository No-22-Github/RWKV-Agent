## Traps
- Answer: 431. TR-DECOY: a substring grep for timeout gives 1036.
- TR-MULTISRC: 6 files; the first one alone gives 78.
- Data volume: 6 data files, 98 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat logs/gateway/*.log | grep -cw timeout` -> 431
Final answer: 431 timeout events (timeouts, timeout_ms and readtimeout lines excluded).

## Why the answer is unique
The README defines the match; one pattern gives one count.
