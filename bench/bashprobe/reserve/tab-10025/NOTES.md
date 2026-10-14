## Traps
- Answer: C1602.
- TR-MULTISRC: 6 files; the first one alone gives A404.
- Data volume: 6 data files, 81 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 物业/电表/*.csv | awk -F, '$4=="居民" {a[$2]+=$3} END {for (k in a) print a[k], k}' | sort -rn | head -3` -> C1602
Final answer: 用电最多的是 C1602。

## Why the answer is unique
类型是精确字段，公摊按 README 排除。
