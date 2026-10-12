## Traps
- TR-DECOY: exact answer 332; the loose match (前缀匹配，含呼入转接) gives 526.
- TR-TRUNC: the file is 58KB and 1449 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F';' '$3=="呼入" && $4+0>600' 话务/calls.dat | wc -l` -> 332
Final answer: 呼入长通话共 332 条。

## Why the answer is unique
类型 is a whole-value column; the duration threshold is strictly greater than 600. The README (话务/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. calls.dat 中呼入通话里超过 600 秒的有几条？
2. 统计类型是呼入、时长大于 600 秒的记录数。
3. 按说明.md，长通话（呼入）的数量是多少？
4. 整月明细里呼入且通话超过十分钟的有多少条？
5. 类型恰好是呼入、时长高于 600 秒的行数。
