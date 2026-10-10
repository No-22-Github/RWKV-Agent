## Traps
- TR-DECOY: receipts 文件里混着两笔 8 月的收款（README 写明属于上月对账单），把全部收款都从 9 月应收里扣会得到 1410.15；正确答案是只扣 9 月收款，差 1545.69。

## Reference solution
1. 查询一：{"path":"data/invoices_2026-09.csv","operation":"sum","field":"fee_gbp"}，得 10841.37。
2. 查询二：{"path":"data/receipts_2026-09.csv","filter":{"value_month":"2026-09"},"operation":"sum","field":"amount_gbp"}，得 9295.68。
3. 相减得 1545.69，终答只报数字。

## Why the answer is unique
decoy 1410.15 把 8 月的收款也扣了，与 README 写明的归属矛盾；两份文件各只有一种按月过滤的读法。答案唯一为 1545.69。
