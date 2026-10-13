## Traps
- Turn 1: 479.
- Turn 2: 121.
- Data volume: 1 data files, 128 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `grep -c ' 月卡=是$' 停车场/进出记录.log` -> 479
Turn 2: bash: `grep ' 月卡=是$' 停车场/进出记录.log | awk '$1 >= "日期=2026-09-21"' | wc -l` -> 121
Final answer (last turn): 21 号起月卡车出场 121 次。

## Why the answer is unique
入口、月卡是精确字段；记录按出场顺序追加。
