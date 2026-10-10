## Traps
- TR-SIGN：扣款列以正数记账，按直觉把扣款加回运费会得 58931.97；README 写明扣款结算时从运费中减去。

## Reference solution
1. 读 README.md：扣款以正数记账、从运费中减去。
2. 查询：{"path":"data/settlement_2026-08.csv","operation":"sum","field":"运费"} 与 {"operation":"sum","field":"扣款"}，相减得 56881.91。
3. 终答只给数字 56881.91。

## Why the answer is unique
README 把扣款的方向钉死为减项，扣款列数值为正只是记账习惯；加回扣款的读法与「扣除扣款后的净结算运费」直接矛盾。答案唯一为 56881.91。
