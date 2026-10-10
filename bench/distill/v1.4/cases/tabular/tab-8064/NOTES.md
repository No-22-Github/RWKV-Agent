## Traps
- 无。

## Reference solution
1. data_query：filter 类别=水产，逐行 数量×单价 求和（或读表后 calculator 逐行相乘相加）。
2. calculator 得 2993.90。
终答示例：水产类 9 月进货合计 2993.90 元（逐行 数量 × 单价 再求和）。。判据：包含 2993.90（千分位 / 去尾零写法均可），调用过 calculator。

## Why the answer is unique
类别过滤精确，金额逐行相乘再加总。
