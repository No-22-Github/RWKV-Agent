## Traps
- Answer: 34899. TR-DECOY: adding 公摊 to the shops gives 68057.
- TR-MULTISRC: 6 files; the first one alone gives 5575.
- Data volume: 6 data files, 88 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 物业/电表/*.csv | awk -F, '$4=="商铺" {s+=$3} END {print s}'` -> 34899
Final answer: 九月商铺合计用电 34899 度。

## Why the answer is unique
类型是精确字段，公摊按 README 排除。
