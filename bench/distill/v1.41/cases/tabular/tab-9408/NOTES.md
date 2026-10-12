## Traps
- TR-DECOY: exact answer 595; the loose reading (工种、班次前缀匹配) gives 1373.
- TR-MULTISRC: 3 files; the first file alone gives 245.

## Reference solution
Turn 1: bash: `cat 工地考勤/*.txt | awk -F'\t' '$2=="钢筋工" && $3=="夜班" {s+=$4} END{print s}'` -> 595
Final answer: 595 小时。

## Why the answer is unique
工种 and 班次 are whole-value columns. The README (工地考勤/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 钢筋工夜班的工时总和是多少？
2. 工种列等于钢筋工、班次列等于夜班的工时相加。
3. 按说明.md，钢筋工（不含学徒）夜班共多少小时？
4. 三个标段里钢筋工夜班累计工时。
5. 把钢筋工夜班的小时数全部加起来，加班夜班不算。
