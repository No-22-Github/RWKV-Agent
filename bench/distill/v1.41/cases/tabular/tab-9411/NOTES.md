## Traps
- TR-DECOY: exact answer 2634; the loose reading (站、油品前缀匹配) gives 5322.
- TR-MULTISRC: 3 files; the first file alone gives 821.

## Reference solution
Turn 1: bash: `cat 加油量/*.txt | awk -F'\t' '$2=="东环站" && $3=="95" {s+=$4} END{print s}'` -> 2634
Final answer: 2634 升。

## Why the answer is unique
站 and 油品 are whole-value columns. The README (加油量/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 东环站 95 号汽油的加油量合计是多少升？
2. 站列等于东环站、油品列等于95的升数之和。
3. 按说明.md，东环站（不含新站）95 号累计多少升？
4. 把东环站95号的加油升数全部相加。
5. 三个班次里东环站的95号汽油总量。
