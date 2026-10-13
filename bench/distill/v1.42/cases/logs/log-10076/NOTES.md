## Traps
- Answer: 753. TR-DECOY: a substring grep for user gives 1780.
- TR-MULTISRC: 6 files; the first one alone gives 133.
- Data volume: 6 data files, 129 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 慢查询/*.log | grep -cw user` -> 753
Final answer: 涉及 user 表的慢 SQL 有 753 条（users、user_profile 等不算）。

## Why the answer is unique
The README defines the match; one pattern gives one count.
