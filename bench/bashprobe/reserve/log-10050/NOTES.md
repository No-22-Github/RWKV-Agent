## Traps
- Turn 1: 386.
- Turn 2: 75.
- TR-MULTISRC: 9 files; the first one alone gives 11.
- Data volume: 9 data files, 171 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat 外卖/评价/*.jsonl | jq -s 'map(select(.["标签"] | index("凉了"))) | length'` -> 386
Turn 2: bash: `cat 外卖/评价/*.jsonl | jq -s 'map(select((.["标签"] | index("凉了")) and .["店铺"]=="阿香米线")) | length'` -> 75
Final answer (last turn): 阿香米线带「凉了」标签的评价有 75 条。

## Why the answer is unique
店铺是精确字符串，评分是整数；说明写明新店分开统计。
