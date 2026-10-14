## Traps
- Answer: 255. TR-DECOY: a substring grep for u12 gives 1072.
- TR-MULTISRC: 8 files; the first one alone gives 33.
- Data volume: 8 data files, 84 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 订单/明细/*.csv | awk -F, '$2=="u12" && $4=="已完成"' | wc -l` -> 255
Final answer: u12 完成了 255 笔订单。

## Why the answer is unique
用户是精确字段，按整字段相等匹配只有一个结果。
