## Traps
- Turn 1: exact answer 33; the loose reading (工种、状态前缀匹配) gives 85.
- Turn 2: exact answer 53; the loose reading (状态前缀匹配，含出勤(半天)) gives 77.
- TR-MULTISRC: 3 files; the first file alone gives 19.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 工地考勤/*.txt | awk -F'\t' '$3=="钢筋工" && $4=="出勤" {print $2}' | sort -u | wc -l` -> 33
Turn 2: bash: `cat 工地考勤/*.txt | awk -F'\t' '$3=="木工" && $4=="出勤" {print $2}' | sort -u | wc -l` -> 53
Final answer: 出勤的木工共 53 人。

## Why the answer is unique
工种 and 状态 are whole-value columns; worker ids are de-duplicated across files. The README (工地考勤/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 木工里出勤过的有多少人（工号去重）？
2. 工种为木工、状态为出勤的不同工号数。
3. 按说明.md，出勤（不含半天）的木工共几人？
4. 三个标段中木工的出勤人数，每个工号只算一次。
5. 统计木工出勤记录里不同工号的个数。
