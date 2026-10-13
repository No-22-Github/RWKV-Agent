## Traps
- Answer: 南3.
- Data volume: 1 data files, 126 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `grep ' 月卡=否$' 停车场/进出记录.log | awk '{print $3}' | sort | uniq -c | sort -rn | head -3` -> 南3
Final answer: 南3。

## Why the answer is unique
入口、月卡是精确字段；记录按出场顺序追加。
