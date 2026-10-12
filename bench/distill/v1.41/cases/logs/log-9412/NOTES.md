## Traps
- TR-DECOY: exact answer 49; the loose reading (渠道、状态前缀匹配) gives 80.
- TR-MULTISRC: 3 files; the first file alone gives 18.

## Reference solution
Turn 1: bash: `cat 民宿订单/*.txt | awk -F';' '$3=="直订" && $4=="已入住" {print $2}' | sort -u | wc -l` -> 49
Final answer: 49 间。

## Why the answer is unique
渠道 and 状态 are whole-value columns; rooms are de-duplicated across files. The README (民宿订单/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 直订并且已入住的房间有几间（去重）？
2. 渠道直订、状态已入住的不同房号个数。
3. 按说明.md，直订入住过的房号共多少个？
4. 三层楼里直订已入住涉及的房间数，同一间只算一次。
5. 统计渠道为直订、状态为已入住的去重房号数。
