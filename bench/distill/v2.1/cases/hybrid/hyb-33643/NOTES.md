## Traps
TR-DEFN

## Reference solution
data_query path=data/orders.csv filter {region: 华东} operation sum expression qty*unit_price. Decoy: summing qty only (212).

## Why the answer is unique
Recomputed from the fixture / fixed clock (2026-09-16 10:00 Asia/Shanghai). Expected: ["num", 77738] 77738

## Five alternative phrasings of the task
1. orders.csv 华东区销售额合计
2. 华东的订单金额一共多少（数量×单价）
3. 统计 data/orders.csv 里华东地区的总收入
4. 华东区卖了多少钱
5. Total revenue for region 华东 in data/orders.csv (qty x unit_price)?
