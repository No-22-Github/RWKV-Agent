## Traps
- TR-DECOY: exact answer 119.4; the loose match (科目包含数学，含数学建模（满分更高）) gives 149.9.
- TR-MULTISRC: 5 files; the first file alone gives 117.3.

## Reference solution
Turn 1: bash: `cat 成绩/*.txt | awk -F'\t' '$3=="数学" && $4+0>m {m=$4+0} END{print m}'` -> 119.4
Final answer: 数学最高分是 119.4。

## Why the answer is unique
科目 is a whole-value column. The README (成绩/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 数学这科全年级最高多少分？
2. 五个班里科目是数学的最高分。
3. 按说明.md，数学（不含数学建模）的最高分是多少？
4. 成绩表中数学成绩的最大值。
5. 所有班级里数学考得最高的分数是多少？
