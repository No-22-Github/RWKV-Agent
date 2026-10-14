## Traps
- Answer: 996. TR-DECOY: an unanchored grep gives 4136.
- TR-MULTISRC: 6 files; the first one alone gives 177.
- Data volume: 6 data files, 83 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 开关/*.conf | grep -c '^启用=是$'` -> 996
Final answer: 生效的有 996 行。

## Why the answer is unique
The README defines the match; one pattern gives one count.
