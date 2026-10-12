## Traps
- TR-MULTISRC: 3 per-region tables; the first alone gives 15983.35.
- TR-DECOY: 「部分已签收」 contains 「已签收」 as a substring; 运单/说明.md says the status is matched exactly, a substring match gives 54497.17.
- TR-DEFN: summing every row regardless of status is far higher.

## Reference solution
1. bash: `cat 运单/2026-09/*.csv | awk -F, '$2=="已签收" {s+=$3} END{printf "%.2f\n", s}'`
Final answer: 九月已签收的运费合计 40617.96 元（状态恰好是「已签收」，部分已签收不算）。

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all 3 files are summed.
