## Traps
- TR-DECOY: exact answer 68; the loose reading (级别前缀匹配，含严重(已恢复)) gives 6.
- TR-TRUNC: the file is 82KB and 1199 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F';' '$3=="严重" {c++; if (c==3) {print NR; exit}}' 告警/设备告警.txt` -> 68
Final answer: 第 3 条严重告警在第 68 行。

## Why the answer is unique
级别 is a whole-value column and the line number counts from the first line of the file. The README (告警/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 设备告警.txt 中第三个「严重」级别的记录是第几行？
2. 把级别恰好是严重的告警按出现顺序数，第 3 条位于哪一行？
3. 按说明.md，第三条严重告警的行号。
4. 严重(已恢复)不算，第 3 条严重告警在文件第几行？
5. 找出级别为严重的第三条记录，告诉我它的行号。
