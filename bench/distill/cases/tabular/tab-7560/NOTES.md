## Traps
- TR-DATEFMT: Coble & Sons 的回款把 value_month 写成 MM/YYYY（README 写明，其余代理是 YYYY-MM）。只按 2026-09 过滤回款会把 Coble & Sons 的款全部漏掉，得 4825.99；把 09/2026 的行也算进来，差额为 2008.07。

## Reference solution
1. 读 README.md：Coble & Sons 用 MM/YYYY，其余代理用 YYYY-MM。
2. 查询一：{"path":"data/charges_2026-09.csv","operation":"sum","field":"fee_gbp"}，得 13896.57。
3. 查询二：{"path":"data/receipts_2026-09.csv","filter":{"value_month":"2026-09"},"operation":"sum","field":"amount_gbp"}，得 9070.58；再对 filter {"value_month":"09/2026"} 求和并相加，得 11888.50。
4. 相减得 2008.07，终答只报数字。

## Why the answer is unique
decoy 4825.99 等于宣布 Coble & Sons 当月分文未收，与 README 写明的月份格式矛盾；两种写法的行互不重叠，9 月之外的月份不存在。答案唯一为 2008.07。
