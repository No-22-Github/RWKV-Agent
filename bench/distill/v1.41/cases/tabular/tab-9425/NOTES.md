## Traps
- TR-DECOY: exact answer 626; the loose reading (不限类型，最长的是主贴) gives 28.
- TR-TRUNC: the file is 129KB and 1167 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="reply" {print length($0), NR}' 评论/评论.dat | sort -rn | head -1` -> 626
Final answer: 最长的回复在第 626 行。

## Why the answer is unique
类型 is a whole-value column; the longest reply line has a strictly greater length than every other reply. The README (评论/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 评论.dat 里回复（reply）最长的那一行是第几行？
2. 只看类型为 reply 的行，整行字符数最大的行号是多少？
3. 按说明.md 的口径，最长回复所在的行号。
4. 主贴不算，哪一行的回复最长？回复它的行号。
5. 找出整行最长的 reply 记录，告诉我它位于文件第几行。
