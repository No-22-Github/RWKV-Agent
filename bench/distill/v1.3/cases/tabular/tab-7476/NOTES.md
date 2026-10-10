## Traps
无陷阱（L0 基题）：费率单一（入库每吨 4.50 元），无例外条款。

## Reference solution
1. 读 README.md 与 notes/fee_standard_2026.txt：入库每吨 4.50 元，年内不作调整。
2. 查询：{"path":"data/rice_intake_sept.csv","operation":"sum","field":"吨位"}，乘以 4.50 得 6981.3。
3. 终答只给数字 6981.3。

## Why the answer is unique
标准文件只有入库一个适用费率且无例外，费率唯一；吨位合计唯一；乘积唯一，答案唯一为 6981.3。
