## Traps
- Answer: 67. TR-DECOY: a substring grep for A1024 gives 273.
- TR-MULTISRC: 6 files; the first one alone gives 13.
- Data volume: 6 data files, 90 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 订单日志/*.log | grep -w A1024 | grep -c 催单` -> 67
Final answer: A1024 被催单 67 次。

## Why the answer is unique
The README defines the match; one pattern gives one count.
