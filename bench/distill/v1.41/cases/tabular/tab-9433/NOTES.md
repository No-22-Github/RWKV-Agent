## Traps
- TR-DECOY: exact answer 1101; the loose reading (账户和差异类型都前缀匹配) gives 1112.
- TR-TRUNC: the file is 59KB and 1111 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F';' '$2=="A-100" && $3=="长款" {n=NR} END{print n}' 对账单/差异.txt` -> 1101
Final answer: A-100 最后一条长款在第 1101 行。

## Why the answer is unique
账户 and 差异类型 are whole-value columns; the file is in append order so the last matching line is unique. The README (对账单/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. A-100 账户最后一次长款出现在文件第几行？
2. 账户是 A-100、差异类型是长款的最后一条记录的行号。
3. 按说明.md，A-100 最末一条长款记录位于哪一行？
4. A-1001 和已调平的不算，A-100 的最后一条长款在第几行？
5. 差异.txt 里 A-100 最近追加的长款记录行号。
