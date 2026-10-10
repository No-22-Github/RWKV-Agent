## Traps
- TR-SIGN: return_gbp 按正数记录（README 写明结算 = 销售额减退货），把退货加进销售额去排名会得到 3304.59；正确答案是按净额排名后的 Nell Perrot，结算合计 2351.60。
- TR-DECOY: 按销售额（毛额）排名的冠军是 Ossie Marsh，毛额合计 2442.42；但题面问结算（净额）最多的 vendor，退货从结算中扣减。

## Reference solution
1. 读 README.md：结算按「销售额 - 退货」，退货按正数记录、结算时扣减。
2. 查询：{"path":"data/resale_2026-09.csv","filter":{"sale_month":"2026-09"},"operation":"sum","expression":"sale_gbp-return_gbp","group_by":"vendor"}，取净额最高的Nell Perrot，得 2351.60。
3. 终答只报数字 2351.60。

## Why the answer is unique
decoy 3304.59 把退货加进了收入，与 README 写明的扣减语义矛盾；decoy 2442.42 是毛额冠军，但净额排名中 Nell Perrot 以 2351.60 居首，且无并列。答案唯一为 2351.60。
