## Traps
- Turn 1: exact answer 156; the loose match (前缀匹配，含逾期已处理) gives 249.
- Turn 2: exact answer 60; the loose match (前缀匹配，含逾期已处理) gives 68.
- TR-MULTISRC: 3 files; the first file alone gives 38.
- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.

## Reference solution
Turn 1: bash: `cat 借阅/*.txt | awk -F'\t' '$3=="逾期"' | wc -l` -> 156
Turn 2: bash: `cat 借阅/*.txt | awk -F'\t' '$3=="逾期" {print $1}' | sort -u | wc -l` -> 60
Final answer: 逾期涉及 60 个不同的借书证。

## Why the answer is unique
状态 is a whole-value column and 借书证 identifies a reader across files. The README (借阅/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 有逾期记录的读者（按借书证）一共多少人？
2. 状态是逾期的记录里，不重复的借书证有多少个？
3. 三个分馆合起来，有多少个借书证存在逾期？
4. 按说明.md，逾期读者的人数是多少？
5. 逾期记录对应的借书证去重后有几个？
