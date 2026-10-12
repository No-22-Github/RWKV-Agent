## Traps
- TR-DECOY: exact answer 612; the loose match (前缀匹配，首个是蓝牙耳机) gives 122.
- TR-TRUNC: the file is 56KB and 967 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F'\t' '$1=="蓝牙" {print NR; exit}' 词典/词表.txt` -> 612
Final answer: 词条「蓝牙」第一次出现在第 612 行。

## Why the answer is unique
词条 is a whole-value column, the header is line 1, and the first exact entry is unique. The README (词典/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 词表里「蓝牙」这个词条首次出现在哪一行？
2. 词表.txt 中词条等于蓝牙的最早一行是第几行（表头算第1行）？
3. 按说明.md，找出蓝牙第一次作为独立词条出现的行号。
4. 「蓝牙」（不是蓝牙耳机）在词表的第几行第一次出现？
5. 给我词条列恰好为蓝牙的第一行行号。
