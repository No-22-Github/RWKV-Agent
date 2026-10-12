## Traps
- TR-DECOY: exact answer 38452; the loose reading (坐席、类型前缀匹配) gives 81318.
- TR-MULTISRC: 3 files; the first file alone gives 10451.

## Reference solution
Turn 1: bash: `cat 外呼记录/*.txt | awk -F, '$2=="A07" && $3=="外呼" {s+=$4} END{print s}'` -> 38452
Final answer: 38452 秒。

## Why the answer is unique
坐席 and 类型 are whole-value columns. The README (外呼记录/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. A07 坐席外呼的通话总秒数是多少？
2. 坐席列等于 A07、类型列等于外呼的秒数之和。
3. 按说明.md，A07 纯外呼累计通话多少秒？
4. 把 A07 的外呼秒数加起来，转接不算。
5. 三个班次里 A07 外呼时长合计。
