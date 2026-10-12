## Traps
- TR-DECOY: exact answer 1180; the loose reading (主机和事件都前缀匹配，含web-010和重启中) gives 1279.
- TR-TRUNC: the file is 69KB and 1279 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk '$2=="web-01" && $3=="重启" {n=NR} END{print n}' 运行/事件.txt` -> 1180
Final answer: web-01 最后一次重启在第 1180 行。

## Why the answer is unique
主机 and 事件 are whole-value columns; the last matching line is unique. The README (运行/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. web-01 最近一次重启记录的行号是多少？
2. 事件列等于重启、主机列等于 web-01 的最后一行是第几行？
3. 按说明.md，web-01 的最后一次重启出现在第几行？
4. web-010 和重启中都不算，web-01 末次重启的行号。
5. 事件.txt 里 web-01 最晚的一条重启事件位于哪一行？
