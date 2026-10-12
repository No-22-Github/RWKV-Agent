## Traps
- TR-MULTISRC: five store files. TR-DECOY: 「奶茶杯套」 shares the prefix; 退货 and 赠送 rows must not count as sales (and sales rows are not returns).
- Turn 2 asks a different type (347 cups returned) over the same files, so turn 1's number (1490) is the wrong answer.

## Reference solution
Turn 1: bash: `cat 流水/*.csv | awk -F, '$2=="奶茶" && $4=="销售" {s+=$3} END{print s}'` -> 1490
Turn 2: bash: `cat 流水/*.csv | awk -F, '$2=="奶茶" && $4=="退货" {s+=$3} END{print s}'` -> 347
Final answers: 奶茶卖出 1490 杯；退货 347 杯.

## Why the answer is unique
品类 and 类型 are exact fields; 流水/说明.md fixes the unit as cups.

## Five alternative phrasings of the task
1. 退货的奶茶共多少杯
2. 各门店奶茶退货数量合计
3. 奶茶被退了多少杯（全部门店）
4. 统计所有门店退回的奶茶杯数
5. How many cups of 奶茶 were returned across all stores?
