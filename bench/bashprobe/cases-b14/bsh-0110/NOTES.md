## Traps
- Answer: 27. TR-DECOY: counting the intern posting gives 44.
- TR-MULTISRC: 8 files; the first one alone gives 2.
- Data volume: 8 data files, 160 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat 招聘/投递/*.jsonl | jq -s 'map(select(.["岗位"]=="后端工程师" and .["阶段"]=="终面")) | length'` -> 27
Final answer: 后端工程师进入终面的有 27 人（实习岗不算）。

## Why the answer is unique
岗位和阶段是精确字段，口径文件写明实习岗位单独统计。
