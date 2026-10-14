## Traps
- Turn 1: 587. TR-DECOY: a substring grep gives 1185.
- Turn 2: 192.
- TR-MULTISRC: 6 files; the first one alone gives 34.
- Data volume: 6 data files, 93 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat jobs/logs/*.log | grep -cw retry` -> 587
Turn 2: bash: `cat jobs/logs/*.log | grep -w retry | grep -c 'job=billing'` -> 192
Final answer (last turn): 192 of them are from the billing job.

## Why the answer is unique
The README defines the match; one pattern gives one count.
