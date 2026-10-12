## Traps
- Turn 1: exact answer 55; the loose reading (车型、出口前缀匹配) gives 109.
- Turn 2: exact answer 30; the loose reading (出口前缀匹配，含东门(应急)) gives 43.
- TR-MULTISRC: 3 files; the first file alone gives 10.
- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.

## Reference solution
Turn 1: bash: `cat 停车场/*.txt | awk -F',' '$3=="新能源" && $4=="东门" {print $2}' | sort -u | wc -l` -> 55
Turn 2: bash: `cat 停车场/*.txt | awk -F',' '$3=="货车" && $4=="东门" {print $2}' | sort -u | wc -l` -> 30
Final answer: 东门出场的货车共 30 辆。

## Why the answer is unique
车型 and 出口 are whole-value columns; plates are de-duplicated across files. The README (停车场/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 东门出场的货车有几辆（车牌去重）？
2. 三个文件里车型为货车、出口为东门的不同车牌数量。
3. 按说明.md，东门（不含应急）出场的货车共多少辆？
4. 统计经东门出场的不同货车车牌数。
5. 东门出口的货车去重后是多少辆？
