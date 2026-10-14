## Traps
- Answer: 猎头.
- Data volume: 8 data files, 150 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 招聘/投递/*.jsonl | jq -s 'map(select(.["阶段"]=="offer")) | group_by(.["渠道"]) | map({c: .[0]["渠道"], n: length}) | sort_by(-.n) | .[0:3]'` -> 猎头
Final answer: offer 最多的渠道是 猎头。

## Why the answer is unique
岗位和阶段是精确字段，口径文件写明实习岗位单独统计。
