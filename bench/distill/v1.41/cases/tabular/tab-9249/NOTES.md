## Traps
- TR-DECOY: exact answer 5999; the loose match (窗口包含3号窗口，含13号窗口和外卖) gives 12428.
- TR-MULTISRC: 3 files; the first file alone gives 2314.

## Reference solution
Turn 1: bash: `cat 食堂/*.txt | awk -F'\t' '$3=="3号窗口" {s+=$4} END{print s}'` -> 5999
Final answer: 3号窗口营业额 5999 元。

## Why the answer is unique
窗口 is a whole-value column. The README (食堂/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 3号窗口这三天卖了多少钱？
2. 统计窗口为3号窗口的金额总和（元）。
3. 按说明.md，3号窗口三天营业额合计是多少？
4. 刷卡记录里3号窗口（不含外卖）的金额加起来是多少元？
5. 三份食堂记录中3号窗口的总收入。
