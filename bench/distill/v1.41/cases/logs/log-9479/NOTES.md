## Traps
- Turn 1: exact answer 1846; the loose reading (车号、动作前缀匹配) gives 4090.
- Turn 2: exact answer 1935; the loose reading (车号前缀匹配，含F-030) gives 2733.
- Turn 3: exact answer 207; the loose reading (车号前缀匹配，含F-03、F-030) gives 1728.
- TR-TRUNC: the file is 84KB and 1274 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk -F';' '$2=="F-03" && $3=="入库" {s+=$4} END{print s}' 叉车作业/作业.dat` -> 1846
Turn 2: bash: `awk -F';' '$2=="F-03" && $3=="出库" {s+=$4} END{print s}' 叉车作业/作业.dat` -> 1935
Turn 3: bash: `awk -F';' '$2=="F-05" && $3=="出库" {a+=$4} $2=="F-03" && $3=="出库" {b+=$4} END{d=a-b; if (d<0) d=-d; print d}' 叉车作业/作业.dat` -> 207
Final answer: F-05 与 F-03 的出库托盘数相差 207。

## Why the answer is unique
车号 and 动作 are whole-value columns. The README (叉车作业/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. F-05 出库托盘数和 F-03 的差多少？
2. 算出 F-05 的出库托盘数，再给我它与 F-03 的差值。
3. 两台车（F-05、F-03）出库托盘数相差几个？
4. F-05 比 F-03 多或少出库多少托盘，取绝对值。
5. F-05 出库合计减去 F-03 出库合计，绝对值是多少？
