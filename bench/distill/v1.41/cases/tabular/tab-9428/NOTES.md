## Traps
- TR-DECOY: exact answer 59.9; the loose reading (含校准中的无效读数) gives 97.8.
- TR-TRUNC: the file is 65KB and 1291 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F, '$2=="S-07" && $4=="正常" && ($3+0>m || m=="") {m=$3+0} END{print m}' 温控/探头.txt` -> 59.9
Final answer: S-07 的最高有效温度是 59.9 度。

## Why the answer is unique
探头 and 状态 are whole-value columns; the maximum valid reading is unique. The README (温控/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. S-07 探头最高的有效温度读数是多少？
2. 状态正常的 S-07 读数里，温度的最大值。
3. 按说明.md，探头 S-07 的最高温度（校准中的不算）。
4. 探头.txt 中 S-07 最热的有效一次是多少度？
5. 统计 S-07 在状态为正常时的温度最大值。
