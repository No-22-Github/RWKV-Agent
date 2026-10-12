## Traps
- TR-MULTISRC: 4 per-region tables; the first alone gives 13271.50.
- TR-DECOY: 「已通过待复核」 contains 「已通过」 as a substring; 报销/说明.md says the status is matched exactly, a substring match gives 74463.11.
- TR-DEFN: summing every row regardless of status is far higher.

## Reference solution
1. bash: `cat 报销/2026Q3/*.csv | awk -F, '$2=="已通过" {s+=$3} END{printf "%.2f\n", s}'`
Final answer: 三季度已通过的报销金额合计 45750.19 元（只算状态恰好是「已通过」的单据，待复核的不计）。

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all 4 files are summed.
