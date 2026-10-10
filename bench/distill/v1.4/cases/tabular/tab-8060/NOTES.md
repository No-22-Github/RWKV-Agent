## Traps
- 各书退货率求平均会得到另一个数

## Reference solution
1. data_query：filter 经销商=知行图书，sum 发货册数 与 退货册数。
2. calculator：退货合计 / 发货合计 * 100，precision 1 → 9.9。
终答示例：知行图书整体退货率约 9.9%（退货总册数 ÷ 发货总册数）。。判据：包含 9.9（千分位 / 去尾零写法均可），调用过 calculator。

## Why the answer is unique
口径是总量比总量，不是各书退货率平均。
