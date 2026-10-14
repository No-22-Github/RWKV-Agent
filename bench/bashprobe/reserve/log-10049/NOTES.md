## Traps
- Answer: 老街面馆（新店）.
- TR-MULTISRC: 9 files; the first one alone gives 老街面馆.
- Data volume: 9 data files, 169 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 外卖/评价/*.jsonl | jq -s 'map(select(.["评分"]==5)) | group_by(.["店铺"]) | map({s: .[0]["店铺"], n: length}) | sort_by(-.n) | .[0:3]'` -> 老街面馆（新店）
Final answer: 五星最多的是 老街面馆（新店）。

## Why the answer is unique
店铺是精确字符串，评分是整数；说明写明新店分开统计。
