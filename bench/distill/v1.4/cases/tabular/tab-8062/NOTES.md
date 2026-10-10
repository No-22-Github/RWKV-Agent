## Traps
- 无。

## Reference solution
1. data_query：设备=EQ-07 求 开机小时 之和。
2. calculator：合计 × 132.5，precision 2 → 11050.50。
终答示例：11050.50。判据：expected_number 11050.50，调用过 calculator。

## Changelog
- v2：S5：题面去掉「一共开机多少小时」——同时问两个量又要求「只回数字」，三遍老师都回了两个数（83.4 11050.50），纯数字判据必挂。

## Why the answer is unique
表内每台设备正好 14 天，设备编号精确。
