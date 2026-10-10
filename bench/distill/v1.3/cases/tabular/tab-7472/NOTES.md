## Traps
无陷阱（L0 基题）：两表各求和后相减，方向由题面写明。

## Reference solution
1. 读 README.md：台账记应收，流水记实收。
2. 查询两表分别求和：{"path":"data/ledger_2026-08.csv","operation":"sum","field":"应收金额"} 与 {"path":"data/receipts_2026-08.csv","operation":"sum","field":"实收金额"}，相减得 1773.24。
3. 终答只给数字 1773.24。

## Why the answer is unique
题面把方向写成「应收比实收多多少」，两表口径由 README 钉死，差额只有一种结果，答案唯一。
