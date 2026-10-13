## Traps
- Answer: 161.
- TR-MULTISRC: 6 files; the first one alone gives 32.
- Data volume: 6 data files, 84 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 物业/电表/*.csv | awk -F, '$4=="居民" && $3>=90 {print $2}' | sort -u | wc -l` -> 161
Final answer: 有 161 户居民出现过单日 ≥90 度。

## Why the answer is unique
类型是精确字段，公摊按 README 排除。
