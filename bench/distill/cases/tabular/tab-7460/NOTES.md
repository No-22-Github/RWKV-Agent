## Traps
无陷阱（L0 基题）：过滤后去重计数。

## Reference solution
1. 读 README.md：每行一张订单，客户类型分单位、个人。
2. 查询：{"path":"data/orders_2026-08.csv","filter":{"客户类型":"单位"},"operation":"distinct_count","field":"客户"}，得 7.0。
3. 终答只给数字 7.0。

## Why the answer is unique
「多少家」问的是去重后的客户数，单位客户在表中多行出现，按客户列去重只有一种结果，答案唯一。
