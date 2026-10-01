## Traps
无陷阱（L0 基题）：全表求平均。

## Reference solution
1. 读 README.md：每行一张订单，金额为实收。
2. 查询：{"path":"data/drygoods_orders_2026-04.csv","operation":"sum","field":"金额"} 与 {"operation":"count"}，再相除得 286.4。
3. 终答只给数字 286.4。

## Why the answer is unique
平均单笔金额 = 金额合计除以行数，文件只含这 18 张订单，分母没有第二种口径，答案唯一。
