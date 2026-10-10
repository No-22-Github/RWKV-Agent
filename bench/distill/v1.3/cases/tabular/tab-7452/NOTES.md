## Traps
无陷阱（L0 基题）：单列过滤后求和。

## Reference solution
1. 读 README.md：每行一笔收银小票，渠道共三种。
2. 查询：{"path":"data/cafe_sales_2026-09.csv","filter":{"渠道":"外带"},"operation":"sum","field":"金额"}，得 1467.0。
3. 终答只给数字 1467.0。

## Why the answer is unique
过滤条件渠道=外带唯一确定一组行，其余两渠道不在口径内，逐行求和只有一种结果。
