## Traps
- Answer: 34. TR-DECOY: counting the new branch gives 88.
- TR-MULTISRC: 9 files; the first one alone gives 3.
- Data volume: 9 data files, 181 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 外卖/评价/*.jsonl | jq -s 'map(select(.["店铺"]=="老街面馆" and .["评分"]<=2)) | length'` -> 34
Final answer: 老街面馆差评（≤2 星）34 条，新店不算。

## Why the answer is unique
店铺是精确字符串，评分是整数；说明写明新店分开统计。
