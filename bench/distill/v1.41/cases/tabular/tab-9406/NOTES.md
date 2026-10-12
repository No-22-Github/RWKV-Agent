## Traps
- TR-DECOY: exact answer 77; the loose reading (科室、状态前缀匹配) gives 170.
- TR-MULTISRC: 5 files; the first file alone gives 17.

## Reference solution
Turn 1: bash: `cat 门诊挂号/*.txt | awk -F'\t' '$2=="内科" && $3=="已就诊"' | wc -l` -> 77
Final answer: 77 条。

## Why the answer is unique
科室 and 状态 are whole-value columns. The README (门诊挂号/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 内科已就诊（不含急诊和复诊）共几条？
2. 五天里科室是内科且状态是已就诊的行数。
3. 按说明.md，普通内科的就诊记录总数是多少？
4. 统计内科已就诊挂号的条数。
5. 科室列为内科、状态列为已就诊的记录有多少。
