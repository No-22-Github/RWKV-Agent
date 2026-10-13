## Traps
- Answer: 489000.
- TR-MULTISRC: 8 files; the first one alone gives 100000.
- Data volume: 8 data files, 155 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 招聘/投递/*.jsonl | jq -s 'map(select(.["阶段"]=="offer" and .["岗位"]=="数据分析师") | .["期望月薪"]) | add'` -> 489000
Final answer: 合计 489000 元/月。

## Why the answer is unique
岗位和阶段是精确字段，口径文件写明实习岗位单独统计。
