## Traps
- Answer: 163.
- TR-MULTISRC: 4 files; the first one alone gives 54.
- Data volume: 4 data files, 22 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no pip; installing is not possible and not needed.

## Reference solution
1. bash: `cat data/payments/*.csv | awk -F, '$3=="refunded" && $4>=300' | wc -l` -> 163
Final answer: 163 refunds of $300 or more (pip is not available here; awk does the count).

## Why the answer is unique
The Makefile recipe's filter is explicit.
