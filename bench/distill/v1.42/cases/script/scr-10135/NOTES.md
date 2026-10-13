## Traps
- Answer: 686.
- TR-MULTISRC: 4 files; the first one alone gives 162.
- Data volume: 4 data files, 19 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no python3, so running 工时/加班统计.py fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat 工时/*.csv | awk -F, '$3=="加班" {s+=$4} END {print s}'` -> 686
Final answer: 加班统计.py 会输出 686 小时（只算类型=加班）。

## Why the answer is unique
脚本只累加类型为加班的小时数。
