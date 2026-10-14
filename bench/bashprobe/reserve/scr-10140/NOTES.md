## Traps
- Answer: 175023.
- TR-MULTISRC: 4 files; the first one alone gives 43986.
- Data volume: 4 data files, 21 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no make, so running Makefile fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat data/payments/*.csv | awk -F, '$3=="paid" {s+=$4} END {print s}'` -> 175023
Final answer: make revenue would print 175023; make isn't installed, so I ran its recipe's logic directly.

## Why the answer is unique
The Makefile recipe's filter is explicit.
