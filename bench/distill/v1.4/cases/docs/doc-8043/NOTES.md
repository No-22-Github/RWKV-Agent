## Traps
- 小时折算方式只在合同里；整天计 7 天会多收

## Reference solution
1. read_file 租赁/超声设备合同.md：日租金 515 元，不足一天按小时折算（日租金 ÷ 24 × 小时数）。
2. calculator：515 * (6 + 19/24) = 3497.71。
终答示例：3497.71。判据：expected_number 3497.71，调用过 calculator。

## Why the answer is unique
不足一天部分按日租金 ÷ 24 逐小时计。
