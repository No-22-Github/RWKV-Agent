## Traps
- Turn 1: 34572.
- Turn 2: 11262.
- Data volume: 3 data files, 18 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no make, so running Makefile fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
Turn 1: bash: `cat 库存/*.csv | awk -F, '$4=="可用" {s+=$3} END {print s}'` -> 34572
Turn 2: bash: `awk -F, '$4=="可用" {s+=$3} END {print s}' 库存/华东仓.csv` -> 11262
Final answer (last turn): 华东可用 目标会输出 11262。

## Why the answer is unique
Makefile 里的 awk 条件写得很明确。
