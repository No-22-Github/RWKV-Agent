## Traps
- Answer: 17427.88. TR-DECOY: a substring grep for u12 gives 77062.26.
- TR-MULTISRC: 8 files; the first one alone gives 2089.36.
- Data volume: 8 data files, 80 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 订单/明细/*.csv | awk -F, '$2=="u12" && $4=="已取消" {s+=$3} END {printf "%.2f\n", s}'` -> 17427.88
Final answer: u12 已取消订单合计 17427.88 元。

## Why the answer is unique
用户是精确字段，按整字段相等匹配只有一个结果。
