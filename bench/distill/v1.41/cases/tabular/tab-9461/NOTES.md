## Traps
- Turn 1: exact answer 2162; the loose reading (药品、状态前缀匹配) gives 4252.
- Turn 2: exact answer 544; the loose reading (药品、状态前缀匹配) gives 858.
- Turn 3: exact answer 196; the loose reading (药品、状态前缀匹配) gives 75.
- TR-MULTISRC: 3 files; the first file alone gives 91.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 药房出库/*.txt | awk -F'\t' '$2=="阿莫西林" && $5=="已发" {s+=$4} END{print s}'` -> 2162
Turn 2: bash: `cat 药房出库/*.txt | awk -F'\t' '$2=="阿莫西林" && $5=="已发" && $3=="急诊" {s+=$4} END{print s}'` -> 544
Turn 3: bash: `cat 药房出库/*.txt | awk -F'\t' '$2=="阿莫西林" && $5=="已发" && $3=="儿科" {a+=$4} $2=="阿莫西林" && $5=="已发" && $3=="急诊" {b+=$4} END{d=a-b; if (d<0) d=-d; print d}'` -> 196
Final answer: 儿科和急诊的已发数量合计相差 196 盒。

## Why the answer is unique
药品 and 状态 are whole-value columns of the tab-separated tables. The README (药房出库/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 儿科的已发合计和急诊的差是多少盒？
2. 算出儿科已发数量，再告诉我它与急诊相差多少。
3. 儿科与急诊两个科室的阿莫西林已发数量差额。
4. 同样口径下儿科比急诊多或少多少盒（取差的绝对值）？
5. 儿科已发数量合计减去急诊的，差距有多大？
