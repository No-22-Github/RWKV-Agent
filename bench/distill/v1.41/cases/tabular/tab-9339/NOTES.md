## Traps
- TR-DECOY: exact answer 84946; the loose reading (整行包含AC-1，含AC-11和备注) gives 140487.
- TR-TRUNC: the file is 82KB and 1387 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk '$2=="AC-1" {s+=$3} END{print s}' 能耗/抄表.txt` -> 84946
Final answer: AC-1 本月合计 84946 度。

## Why the answer is unique
设备 is a whole-value column; AC-1 elsewhere in the line does not count. The README (能耗/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. AC-1 空调这个月一共用了多少度电？
2. 抄表记录中设备列等于 AC-1 的度数之和。
3. 按说明.md，AC-1（不含 AC-11）的用电度数合计。
4. 整月抄表里 AC-1 的度数总和是多少？
5. 统计设备为 AC-1 的所有行的度数列合计。
