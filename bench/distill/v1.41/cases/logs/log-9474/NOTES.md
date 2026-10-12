## Traps
- Turn 1: exact answer 102; the loose reading (大棚、事件前缀匹配) gives 143.
- Turn 2: exact answer 44; the loose reading (大棚前缀匹配，含3号东) gives 63.
- TR-TRUNC: the file is 92KB and 1343 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk '$2=="3号" && $4=="告警" {print $3}' 温室/记录.txt | sort -u | wc -l` -> 102
Turn 2: bash: `awk '$2=="3号" && $4=="维护" {print $3}' 温室/记录.txt | sort -u | wc -l` -> 44
Final answer: 3号大棚维护过的设备共 44 台。

## Why the answer is unique
大棚 and 事件 are whole-value columns; devices are de-duplicated. The README (温室/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 3号大棚里有多少台设备做过维护？
2. 大棚为3号、事件为维护的不同设备数。
3. 按说明.md，3号棚（不含3号东）维护的设备去重后多少台？
4. 统计3号大棚维护事件涉及的设备台数，每台只算一次。
5. 记录里3号大棚被维护过的不同设备个数。
