## Traps
- TR-DECOY: exact answer 1749.4; the loose match (前缀匹配，含60051) gives 2097.5.
- TR-TRUNC: the file is 40KB and 1315 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="600519" && $3+0>m {m=$3+0} END{print m}' 行情/prices.dat` -> 1749.4
Final answer: 600519 最高收盘价 1749.4。

## Why the answer is unique
代码 is a whole-value column. The README (行情/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 600519 的收盘价最大值是多少？
2. prices.dat 里代码为 600519 的最高收盘价。
3. 按说明.md，600519 历史最高收盘价是多少？
4. 代码 600519（不是60051）最高收过多少？
5. 行情文件中 600519 的最大收盘价。
