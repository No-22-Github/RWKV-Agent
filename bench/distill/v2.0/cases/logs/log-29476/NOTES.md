## Traps
- Turn 1: exact answer 147; the loose reading (线路包含7路、卡类型前缀匹配) gives 233.
- Turn 2: exact answer 84; the loose reading (线路包含7路，含17路、27路) gives 144.
- TR-TRUNC: the file is 94KB and 1295 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `awk -F'\t' '$2=="7路" && $4=="成人卡" {print $3}' 公交刷卡/刷卡.txt | sort -u | wc -l` -> 147
Turn 2: bash: `awk -F'\t' '$2=="7路" && $4=="学生卡" {print $3}' 公交刷卡/刷卡.txt | sort -u | wc -l` -> 84
Final answer: 7路上刷过学生卡的不同卡号共 84 个。

## Why the answer is unique
线路 and 卡类型 are whole-value columns; card numbers are de-duplicated. The README (公交刷卡/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 7路学生卡刷了多少张不同的卡？
2. 线路7路、卡类型学生卡的卡号去重数量。
3. 按说明.md，7路（不含17路、27路）的学生卡有几张不同的卡？
4. 统计7路上学生卡的不同卡号个数。
5. 刷卡.txt 中7路的学生卡，去重后是多少张？
