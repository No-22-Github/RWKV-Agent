## Traps
TR-DEFN

## Reference solution
data_query filter warehouse=B, sum with expression stock*price. Summing stock only is the decoy.

## Why the answer is unique
Recomputed from the fixture / fixed clock (2026-09-16 10:00 Asia/Shanghai). Expected: ["num", 134075.6] 134075.6

## Five alternative phrasings of the task
1. Warehouse B inventory value from inventory.csv
2. Sum of stock*price for warehouse B
3. How much is the stock in warehouse B worth?
4. inventory.csv: total worth of B warehouse stock
5. B 仓库的库存总价值是多少（库存×单价）
