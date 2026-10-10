## Traps
- TR-SIGN：积分抵扣以正数记录，按直觉把抵扣加回工时费会得 29213.69；README 写明抵扣结算时从工时费中扣减。

## Reference solution
1. 读 README.md：积分抵扣以正数记录、从工时费中扣减。
2. 查询：{"path":"data/repairs_2026-09.csv","operation":"sum","field":"工时费"} 与 {"operation":"sum","field":"积分抵扣"}，相减得 28350.83。
3. 终答只给数字 28350.83。

## Why the answer is unique
README 把抵扣的方向钉死为减项，列中数值为正只是记账习惯；加回抵扣的读法与「扣除积分抵扣后的净收入」直接矛盾。答案唯一为 28350.83。
