## Traps
- 费率只在配置里；急件加价 20% 题面没提，不用

## Reference solution
1. read_file 灭菌/外包费率.yaml：per_piece_yuan 0.85，base_fee_per_batch_yuan 120。
2. calculator：(320 + 450 + 275) * 0.85 + 3 * 120 = 1248.25。
终答示例：1248.25。判据：expected_number 1248.25，调用过 calculator。

## Why the answer is unique
起步费按批次收，单价按件收，三批三次。
