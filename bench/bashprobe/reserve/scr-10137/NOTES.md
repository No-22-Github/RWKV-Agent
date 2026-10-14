## Traps
- Turn 1: 393792.
- Turn 2: 110538.
- TR-MULTISRC: 3 files; the first one alone gives 0.
- Data volume: 3 data files, 55 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no node, so running 销售/汇总.js fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
Turn 1: bash: `cat 销售/*.jsonl | jq -s 'map(select(.["月份"]=="2026-08") | .["金额"]) | add'` -> 393792
Turn 2: bash: `cat 销售/*.jsonl | jq -s 'map(select(.["月份"]=="2026-08" and .["区域"]=="华南") | .["金额"]) | add'` -> 110538
Final answer (last turn): 加上 --区域 华南 后结果是 110538 元。

## Why the answer is unique
脚本按月份参数筛选后求和。
