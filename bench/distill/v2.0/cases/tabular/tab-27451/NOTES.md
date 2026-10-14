## Traps
无陷阱（L0 基题）：数据干净，单表求和。

## Reference solution
1. 读 README.md：每行一笔销售小票，金额为实收。
2. 查询：{"path":"data/tea_sales_2026-08.csv","operation":"sum","field":"金额"}，得 29062.0。
3. 终答只给数字 29062.0。

## Why the answer is unique
题面问的是 2026 年 8 月全部销售额，文件只含 8 月数据，逐行求和只有一种结果。无重复行、无干扰列，答案唯一。
