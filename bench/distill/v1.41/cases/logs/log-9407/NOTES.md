## Traps
- TR-DECOY: exact answer 58; the loose reading (课程、出勤前缀匹配) gives 91.
- TR-MULTISRC: 4 files; the first file alone gives 21.

## Reference solution
Turn 1: bash: `cat 健身房/*.txt | awk -F';' '$3=="瑜伽" && $4=="到课" {print $2}' | sort -u | wc -l` -> 58
Final answer: 58 位。

## Why the answer is unique
课程 and 出勤 are whole-value columns; members are de-duplicated across files. The README (健身房/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 上过瑜伽课（到课）的不同会员有多少人？
2. 瑜伽、到课两个条件下去重的会员数。
3. 按说明.md，正式到课的瑜伽会员有几位？
4. 四天里瑜伽到课会员的去重人数。
5. 统计课程是瑜伽、出勤是到课的不同会员数量。
