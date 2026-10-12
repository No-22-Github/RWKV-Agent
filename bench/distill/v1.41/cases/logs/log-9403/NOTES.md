## Traps
- TR-DECOY: exact answer 34; the loose reading (活动、状态前缀匹配) gives 56.
- TR-MULTISRC: 4 files; the first file alone gives 12.

## Reference solution
Turn 1: bash: `cat 志愿服务/*.txt | awk -F'\t' '$3=="植树" && $4=="完成" {print $2}' | sort -u | wc -l` -> 34
Final answer: 34 位。

## Why the answer is unique
活动 and 状态 are whole-value columns; volunteers are de-duplicated across files. The README (志愿服务/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 完成植树活动的不同志愿者有几位？
2. 植树、完成这两个条件下去重后的志愿者人数。
3. 按说明.md，植树完成的志愿者共多少人（去重）？
4. 四个月里正式完成植树的志愿者数量，同一个人只数一次。
5. 统计活动是植树、状态是完成的不同志愿者人数。
