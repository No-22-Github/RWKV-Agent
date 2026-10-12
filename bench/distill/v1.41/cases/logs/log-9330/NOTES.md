## Traps
- TR-DECOY: exact answer 31; the loose reading (打印机和事件都用前缀匹配) gives 72.
- TR-MULTISRC: 3 files; the first file alone gives 9.

## Reference solution
Turn 1: bash: `cat 打印日志/*.txt | awk '$2=="P2" && $4=="卡纸" {print $3}' | sort -u | wc -l` -> 31
Final answer: P2 卡纸涉及 31 位不同的用户。

## Why the answer is unique
打印机 and 事件 are whole-value columns; users are de-duplicated across floors. The README (打印日志/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. P2 这台打印机卡纸，涉及多少个不同用户？
2. 三层楼里，在 P2 上遇到卡纸的用户去重后是多少人？
3. 按说明.md，打印机为 P2、事件为卡纸的不同用户数。
4. 有多少位用户在 P2 上发生过卡纸（自己清除的不算）？
5. 统计 P2 卡纸记录里不重复的用户个数。
