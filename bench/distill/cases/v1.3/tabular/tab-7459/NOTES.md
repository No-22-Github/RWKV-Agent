## Traps
无陷阱（L0 基题）：单条件计数。

## Reference solution
1. 读 README.md：每行一张订单，渠道共三种。
2. 查询：{"path":"data/orders_2026-09.csv","filter":{"渠道":"团购"},"operation":"count"}，得 9.0。
3. 终答只给数字 9.0。

## Why the answer is unique
计数口径是行数，过滤条件渠道=团购唯一确定行集合，答案唯一。
