## Traps
- TR-DECOY: Thursday Mixed 的票据张数最多（31 张），但按 lane fee 合计它只有 433.43；题面问收入最高的 league night 的合计，收入最高的是 Tuesday Doubles，共 631.73。张数最多不等于收入最高，按张数最多的夜晚作答不成立。

## Reference solution
1. 查询：{"path":"data/lane_fees_2026-09.csv","filter":{"receipt_month":"2026-09"},"operation":"sum","field":"fee_gbp","group_by":"league_night"}，取合计最高的Tuesday Doubles，得 631.73。
2. 终答只报数字 631.73。

## Why the answer is unique
decoy 433.43 是票据最多的夜晚的合计，但题面问收入最高；分组合计中 Tuesday Doubles 以 631.73 居首，且无并列。答案唯一为 631.73。
