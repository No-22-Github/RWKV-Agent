## Traps
- TR-SIGN: allowance_gbp 按正数记录（README 写明结算时从收入中扣减），把补贴加进收入会得到 24358.01；正确答案是 8 月收入减补贴后的净额 21518.03。

## Reference solution
1. 读 README.md：rework allowance 按正数记录、结算时扣减。
2. 查询：{"path":"data/workroom_2026-08.csv","operation":"sum","expression":"fee_gbp-allowance_gbp"}，得 21518.03。
3. 终答只报数字 21518.03。

## Why the answer is unique
decoy 24358.01 把扣减项加进了收入，与 README 写明的扣减语义矛盾。全表只有一种明细读法，答案唯一为 21518.03。
