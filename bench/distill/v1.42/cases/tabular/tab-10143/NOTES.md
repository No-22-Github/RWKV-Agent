## Traps
- Answer: 35.
- TR-MULTISRC: 4 files; the first one alone gives 5.
- Data volume: 4 data files, 25 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no pip; installing is not possible and not needed.

## Reference solution
1. bash: `cat 账本/*.csv | awk -F, '$2=="招待" && $4=="作废"' | wc -l` -> 35
Final answer: 作废的招待费凭证 35 张（环境没有 pip，这个统计用 awk 就够了）。

## Why the answer is unique
脚本的筛选条件写在源码里；按同一条件复算只有一个结果。
