## Traps
- TR-DECOY: exact answer 217; the loose match (前缀匹配，含异常已处理) gives 312.
- TR-MULTISRC: 4 files; the first file alone gives 47.

## Reference solution
Turn 1: bash: `cat 巡检/*.txt | awk -F'\t' '$4=="异常"' | wc -l` -> 217
Final answer: 异常打卡共 217 条。

## Why the answer is unique
结果 is a whole-value column. The README (巡检/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 巡检记录里结果是异常的有多少次？
2. 四个车间合计，异常（未处理）的打卡条数。
3. 统计结果列恰好等于异常的行数。
4. 按说明.md，十月异常巡检一共几条？
5. 四份巡检表里异常出现了多少次？
