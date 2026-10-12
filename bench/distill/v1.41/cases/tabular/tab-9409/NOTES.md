## Traps
- TR-DECOY: exact answer 183; the loose reading (品名前缀匹配、摊位后缀匹配) gives 90.
- TR-MULTISRC: 3 files; the first file alone gives 191.

## Reference solution
Turn 1: bash: `cat 菜价/*.txt | awk -F, '$2=="西红柿" && $3=="3号" {print $4}' | sort -n | head -1` -> 183
Final answer: 183 分。

## Why the answer is unique
品名 and 摊位 are whole-value columns. The README (菜价/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 3号摊位西红柿最低卖多少分？
2. 品名是西红柿、摊位是3号的单价最小值。
3. 按说明.md，3号摊西红柿（非有机）的最低价。
4. 三个时段里3号摊西红柿的最低单价是多少？
5. 西红柿在3号摊的最低报价是几分？
