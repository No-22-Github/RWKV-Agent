## Traps
- TR-NEARNAME：表里有一对近名列「预订金额 / 实收金额」，猜错列名第一次查询会报错或得 17672.29；README 写明门店实际收到的货款以实收金额为准，预订金额只是下单时报价。

## Reference solution
1. 读 README.md：实收金额是结账实收，门店收到的钱以该列为准。
2. 查询：{"path":"data/store_settlement_2026-09.csv","operation":"sum","field":"实收金额"}，得 17269.29。（若先猜了列名报错，用 select 看列名后改对重查。）
3. 终答只给数字 17269.29。

## Why the answer is unique
两列在多行上数值不同，README 把「实际收到」钉在实收金额上，预订金额的读法与口径相矛盾。月份与门店不设过滤（题面即全部门店九月），答案唯一为 17269.29。
