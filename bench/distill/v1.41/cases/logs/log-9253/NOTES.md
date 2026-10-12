## Traps
- Turn 1: exact answer 62; the loose match (前缀匹配，含WARN-DEPRECATED) gives 118.
- Turn 2: exact answer 191; the loose match (前缀匹配，含ERROR-RETRY) gives 26.
- TR-TRUNC: the file is 91KB and 1213 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="WARN"' 构建/build.txt | wc -l` -> 62
Turn 2: bash: `awk -F'\t' '$2=="ERROR" {print NR; exit}' 构建/build.txt` -> 191
Final answer: 第一条 ERROR 在第 191 行。

## Why the answer is unique
级别 is a whole-value column and build.txt has no header so line numbers equal row numbers. The README (构建/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. build.txt 里最早出现的 ERROR 是哪一行？
2. ERROR 级别的日志第一次出现在第几行（行号从1起）？
3. 按说明.md，首个 ERROR 的行号是多少？
4. 给我 build.txt 中第一条 ERROR 所在的行号。
5. build.txt 的第几行是第一次出现 ERROR。
