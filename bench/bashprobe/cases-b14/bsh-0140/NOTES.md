## Traps
- Answer: 1165465.66.
- TR-MULTISRC: 4 files; the first one alone gives 253704.24.
- Data volume: 4 data files, 24 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no python3, so running 工具/月结.py fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat 账本/*.csv | awk -F, '$4=="已入账" {s+=$3} END {printf "%.2f\n", s}'` -> 1165465.66
Final answer: 月结.py 会输出已入账合计 1165465.66 元——环境里没有 python，我按脚本逻辑用 awk 复算。

## Why the answer is unique
脚本的筛选条件写在源码里；按同一条件复算只有一个结果。
