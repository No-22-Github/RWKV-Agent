## Traps
- TR-DECOY: exact answer 979; the loose reading (站名前缀匹配，含青山闸北) gives 1290.
- TR-MULTISRC: 3 files; the first file alone gives 979.

## Reference solution
Turn 1: bash: `cat 水文站/*.dat | awk '$2=="青山闸" {print $3}' | sort -rn | head -1` -> 979
Final answer: 979 厘米。

## Why the answer is unique
站名 is a whole-value column. The README (水文站/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 青山闸历史最高水位多少厘米？
2. 站名恰好是青山闸的水位最大值。
3. 按说明.md，青山闸（不含青山闸北）的峰值水位是多少？
4. 三个文件里青山闸的最高水位读数。
5. 青山闸水位最高的那条记录是多少厘米？
