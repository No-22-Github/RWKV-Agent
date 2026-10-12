## Traps
- TR-DECOY: exact answer 4795; the loose match (类别包含易碎，含易碎-加固) gives 8900.
- TR-MULTISRC: 4 files; the first file alone gives 4789.

## Reference solution
Turn 1: bash: `cat 快递站/*.txt | awk -F'\t' '$2=="易碎" && $3+0>m {m=$3+0} END{print m}'` -> 4795
Final answer: 易碎类别最重一件 4795 克。

## Why the answer is unique
类别 is a whole-value column; the max is taken over rows whose category is exactly 易碎. The README (快递站/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 易碎件里单件最大重量是多少克？
2. 快递站四天数据中，类别为易碎的最大重量。
3. 按说明.md，易碎类别重量克的最大值是多少？
4. 四个入库表里最重的易碎包裹有多重（克）？
5. 类别恰好是易碎的包裹，最重的是多少克？
