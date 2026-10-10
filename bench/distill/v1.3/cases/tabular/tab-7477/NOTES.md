## Traps
无陷阱（L0 基题）：费率单一（3%），无阶梯与例外。

## Reference solution
1. 读 README.md 与 notes/commission_plan.txt：提成按当月销售额的 3% 计发。
2. 查询：{"path":"data/sales_2026-09.csv","operation":"sum","field":"金额"}，乘以 0.03 得 1139.9763。
3. 终答只给数字 1139.9763。

## Why the answer is unique
提成口径是当月全部销售额乘单一费率，无阶梯无例外，销售额合计唯一，答案唯一为 1139.9763。
