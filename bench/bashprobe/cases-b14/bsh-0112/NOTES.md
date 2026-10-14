## Traps
- Answer: 742.
- TR-MULTISRC: 9 files; the first one alone gives 103.
- Data volume: 9 data files, 175 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 外卖/评价/*.jsonl | jq -s 'map(select(.["有图"]) | .["标签"] | length) | add'` -> 742
Final answer: 带图评价的标签总数是 742 个。

## Why the answer is unique
店铺是精确字符串，评分是整数；说明写明新店分开统计。
