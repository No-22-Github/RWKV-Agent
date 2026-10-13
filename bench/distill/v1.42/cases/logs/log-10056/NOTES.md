## Traps
- Answer: 140.
- Data volume: 1 data files, 128 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `grep ' 车牌=沪C' 停车场/进出记录.log | awk '{split($4, a, "="); if (a[2] > 600) n++} END {print n}'` -> 140
Final answer: 沪C 车牌停留超过 600 分钟的有 140 次。

## Why the answer is unique
入口、月卡是精确字段；记录按出场顺序追加。
