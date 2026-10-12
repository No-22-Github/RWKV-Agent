## Traps
- TR-DECOY: exact answer 1287; the loose reading (员工或备注包含李明、类型前缀匹配) gives 3421.
- TR-TRUNC: the file is 72KB and 1243 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="李明" && $3=="加班" {s+=$4} END{print s+0}' 考勤/工时.txt` -> 1287
Final answer: 李明加班工时合计 1287 小时。

## Why the answer is unique
员工 and 类型 are whole-value columns; remarks mentioning the name do not count. The README (考勤/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 李明这个月加班一共多少小时？
2. 员工是李明、类型是加班的行，工时列求和。
3. 按说明.md，李明（不含李明辉）的加班工时总数。
4. 调休的加班不算，李明的加班小时合计。
5. 工时.txt 里李明的加班工时加起来是多少？
