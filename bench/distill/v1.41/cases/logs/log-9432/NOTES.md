## Traps
- TR-DECOY: exact answer 80; the loose reading (事件前缀匹配，含演练) gives 45.
- TR-TRUNC: the file is 75KB and 1305 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F, '$3=="主备切换" {c++; if (c==4) {print NR; exit}}' 切换/记录.dat` -> 80
Final answer: 第 4 次主备切换在第 80 行。

## Why the answer is unique
事件 is a whole-value column and the line number counts from the first line. The README (切换/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 记录.dat 里第四次主备切换的行号是多少？
2. 演练不算，按出现顺序第 4 条「主备切换」位于哪一行？
3. 按说明.md，第 4 个真实主备切换事件所在行。
4. 事件恰好是主备切换的第四条记录在文件第几行？
5. 找到第四次真正的主备切换，回复它的行号。
