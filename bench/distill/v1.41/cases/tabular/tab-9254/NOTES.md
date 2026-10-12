## Traps
- Turn 1: exact answer 179; the loose match (前缀匹配，含S-07B) gives 325.
- Turn 2: exact answer 31; the loose match (前缀匹配，含S-07B) gives 44.8.
- TR-TRUNC: the file is 38KB and 1306 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.

## Reference solution
Turn 1: bash: `awk -F, '$2=="S-07" && $3+0>20' 传感器/readings.dat | wc -l` -> 179
Turn 2: bash: `awk -F, '$2=="S-07" && $3+0>m {m=$3+0} END{print m}' 传感器/readings.dat` -> 31
Final answer: S-07 最高温度 31 度。

## Why the answer is unique
传感器 is a whole-value column; the temperature comparison is numeric. The README (传感器/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. readings.dat 里 S-07 的最高读数是多少度？
2. S-07（不是 S-07B）的温度最大值。
3. 按说明.md，S-07 记录过的最高温度是多少？
4. S-07 的所有读数里温度最高的是多少度？
5. 传感器 S-07 的峰值温度是多少？
