## Traps
- Turn 1: exact answer 2197; the loose reading (课程前缀匹配，含试听课) gives 3033.
- Turn 2: exact answer 4290; the loose reading (课程前缀匹配，含试听课) gives 6609.
- Turn 3: exact answer 2241; the loose reading (课程前缀匹配，含试听课) gives 2814.
- TR-MULTISRC: 3 files; the first file alone gives 1071.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 网课学习/*.txt | awk -F';' '$3=="Excel入门" && $5=="手机" {s+=$4} END{print s}'` -> 2197
Turn 2: bash: `cat 网课学习/*.txt | awk -F';' '$3=="Excel入门" && $5=="电脑" {s+=$4} END{print s}'` -> 4290
Turn 3: bash: `cat 网课学习/*.txt | awk -F';' '$3=="Excel入门" && $5=="平板" {a+=$4} $3=="Excel入门" && $5=="电脑" {b+=$4} END{d=a-b; if (d<0) d=-d; print d}'` -> 2241
Final answer: 平板和电脑的分钟数合计相差 2241 分钟。

## Why the answer is unique
课程 and 终端 are whole-value columns. The README (网课学习/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 平板上的 Excel入门 学习时长和电脑上的差多少分钟？
2. 算出平板分钟合计，再给我它与电脑合计的差值。
3. 同一门课，平板与电脑两种终端的分钟数相差多少？
4. 平板比电脑多（或少）多少分钟，取绝对值。
5. 电脑合计和平板合计之间的差距是多少分钟？
