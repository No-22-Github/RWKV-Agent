## Traps
- Turn 1: exact answer 18198; the loose match (品名包含螺丝，含螺丝刀) gives 28276.
- Turn 2: exact answer 19636; the loose match (品名包含螺丝，含螺丝刀) gives 29545.
- TR-MULTISRC: 3 files; the first file alone gives 4645.
- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.

## Reference solution
Turn 1: bash: `cat 仓储/*.txt | awk -F'\t' '$2=="螺丝" && $3=="入库" {s+=$4} END{print s}'` -> 18198
Turn 2: bash: `cat 仓储/*.txt | awk -F'\t' '$2=="螺丝" && $3=="出库" {s+=$4} END{print s}'` -> 19636
Final answer: 螺丝出库合计 19636 件。

## Why the answer is unique
品名 and 类型 are exact columns of the tab-separated ledgers. The README (仓储/说明.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. 仓储流水里螺丝一共出库多少件？
2. 三个仓里被领走（出库）的螺丝合计多少件？
3. 螺丝的出库数量总和是多少？
4. 按说明.md的口径，螺丝出库共多少件？
5. 把三份仓单里品名为螺丝、类型为出库的数量加起来。
