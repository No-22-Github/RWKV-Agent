## Traps
- Turn 1: 335.
- Turn 2: 85.
- TR-MULTISRC: 8 files; the first one alone gives 7.
- Data volume: 8 data files, 160 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat 招聘/投递/*.jsonl | jq -s 'map(select(.["渠道"]=="内推")) | length'` -> 335
Turn 2: bash: `cat 招聘/投递/*.jsonl | jq -s 'map(select(.["渠道"]=="内推" and .["阶段"]=="拒绝")) | length'` -> 85
Final answer (last turn): 内推被拒的有 85 人。

## Why the answer is unique
岗位和阶段是精确字段，口径文件写明实习岗位单独统计。
