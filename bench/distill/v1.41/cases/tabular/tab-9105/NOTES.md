## Traps
- TR-MULTISRC: 4 per-group tables; the first alone gives 38750.52.
- TR-DECOY: 「已验收退货」 contains 「已验收」 as a substring; 采购/说明.md says the status is matched exactly, a substring match gives 204472.46.
- TR-DEFN: aggregating every row regardless of status gives 352139.65.

## Reference solution
1. bash: `cat 采购/2026Q3/*.csv | awk -F, '$2=="已验收" {s+=$3} END{printf "%.2f\n", s}'`
Final answer: 三季度已验收的采购金额合计 136617.67 元（只算状态恰好是「已验收」，退货的不计）。

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all 4 files are aggregated.

## Alternative phrasings
1. 三季度四个品类实际花了多少钱？只算已验收的，规则在 采购/说明.md。
2. 采购目录下四张表，状态为已验收的金额加总是多少元？
3. 按采购说明的口径，三季度已验收采购金额一共多少？
4. 把办公、设备、耗材、差旅里已验收的采购单金额加起来。
5. 三季度各品类「已验收」采购单的金额总和是多少元？
