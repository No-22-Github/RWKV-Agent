## Traps
- Turn 1: exact answer 郑可欣; the loose reading (项目包含跳远，含立定跳远、三级跳远) gives 韦承志. Several rows share the extreme value; file order would give 乐知夏, the README rule gives 郑可欣.
- Turn 2: exact answer 赵明轩; the loose reading (项目包含跳远，含跳远和三级跳远) gives 韦承志. Several rows share the extreme value; file order would give 乐知夏, the README rule gives 赵明轩.
- TR-MULTISRC: 3 files; the first file alone gives 施博文.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 校运会/*.txt | awk -F'\t' '$3=="跳远" {print $4, $1, $2}' | sort -k1,1nr -k2,2 | head -1` -> 郑可欣
        then `cat 校运会/*.txt | awk -F'\t' '$3=="跳远"' | wc -l` for the row count asked in the prompt (183)
Turn 2: bash: `cat 校运会/*.txt | awk -F'\t' '$3=="立定跳远" {print $4, $1, $2}' | sort -k1,1nr -k2,2 | head -1` -> 赵明轩
        then `cat 校运会/*.txt | awk -F'\t' '$3=="立定跳远"' | wc -l` for the row count asked in the prompt (165)
Final answer: 立定跳远成绩最好的是赵明轩，立定跳远共有 165 条成绩记录。

## Why the answer is unique
项目 is a whole-value column; the best mark is shared by several athletes and the README picks the smallest entry number. The README (校运会/说明.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. 立定跳远这个项目谁的成绩最高？并列取报名号小的。
2. 三轮成绩里立定跳远的最好成绩是谁创造的？
3. 按说明.md的并列规则，立定跳远冠军是哪位选手？
4. 项目为立定跳远的记录中，最高成绩对应的选手姓名。
5. 立定跳远最远的是谁？成绩相同取报名号最小者。
