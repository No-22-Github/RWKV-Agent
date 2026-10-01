## Traps
- TR-SIGN: deduction_gbp 按正数记录（README 写明结算时从 Hall income 中扣减），把扣减加进收入会得 54571.93；正确答案是 8 月收入减扣减后的净额 45854.75。
- TR-HEADER: 末行是系统生成的当月合计（README 写明不是 trader），对 fee 列整列求和会把合计行算进去，得 100426.68。

## Reference solution
1. 读 README.md：deduction 按正数记录、结算时扣减；末行合计不参与统计。
2. 查询：{"path":"data/register_2026-08.csv","filter":{"entry_month":"2026-08"},"operation":"sum","expression":"fee_gbp-deduction_gbp"}，得 45854.75。
3. 终答只报数字 45854.75。

## Why the answer is unique
decoy 54571.93 把扣减项加进了收入，与 README 写明的扣减语义矛盾；decoy 100426.68 把非trader 的合计行当成了摊位。明细行只有一种读法，答案唯一为 45854.75。
