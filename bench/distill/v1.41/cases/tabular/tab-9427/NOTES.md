## Traps
- TR-DECOY: exact answer 61; the loose reading (项目和结果都前缀匹配) gives 200.
- TR-TRUNC: the file is 68KB and 1252 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk -F';' '$3=="铅" && $4=="超标" {print $1}' 检测/样品检测.txt | sort -u | wc -l` -> 61
Final answer: 铅超标的样品共 61 个。

## Why the answer is unique
项目 and 结果 are whole-value columns; samples repeat across rows and are de-duplicated. The README (检测/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 本月铅检测超标的不同样品有多少个？
2. 项目是铅、结果是超标的记录，样品去重后有几个？
3. 按说明.md，铅超标涉及多少个样品？
4. 铅(溶出)和复测合格的不算，超标的铅样品数量。
5. 统计铅项目超标记录里不同样品的个数。
