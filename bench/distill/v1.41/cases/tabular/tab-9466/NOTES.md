## Traps
- Turn 1: exact answer 53; the loose reading (区域、评价前缀匹配) gives 114.
- Turn 2: exact answer 25; the loose reading (评价前缀匹配，含超时(天气)) gives 32.
- TR-MULTISRC: 4 files; the first file alone gives 8.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 外卖配送/*.txt | awk '$3=="滨江" && $4=="超时" {c++} END{print c+0}'` -> 53
Turn 2: bash: `cat 外卖配送/*.txt | awk '$3=="老城" && $4=="超时" {c++} END{print c+0}'` -> 25
Final answer: 老城超时订单共 25 单。

## Why the answer is unique
区域 and 评价 are whole-value columns. The README (外卖配送/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 老城区域超时的订单有几单？
2. 区域老城、评价超时的记录一共多少条？
3. 按说明.md，老城（天气免责不算）超时订单数量。
4. 四天里老城的超时单数是多少？
5. 统计区域为老城且评价恰好是超时的行数。
