## Traps
- Turn 1: exact answer 65; the loose reading (城区包含东城、结果前缀匹配) gives 86.
- Turn 2: exact answer 34; the loose reading (城区包含东城、结果前缀匹配，含拒单(系统)) gives 98.
- TR-MULTISRC: 4 files; the first file alone gives 12.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 派单/*.txt | awk '$3=="东城" && $4=="接单" {print $2}' | sort -u | wc -l` -> 65
Turn 2: bash: `cat 派单/*.txt | awk '$3=="东城" && $4=="拒单" {print $2}' | sort -u | wc -l` -> 34
Final answer: 东城拒单的不同司机共 34 位。

## Why the answer is unique
城区 and 结果 are whole-value columns; drivers are de-duplicated across the four files. The README (派单/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 东城区拒过单的司机有几位？
2. 四天里城区为东城、结果为拒单的不同司机数量。
3. 按说明.md，东城拒单的司机去重后是多少人？
4. 在东城拒绝过订单的司机共有多少位？
5. 统计东城拒单记录涉及的不同司机人数。
