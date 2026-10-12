## Traps
- TR-MULTISRC: 4 per-region tables; the first alone gives 10525.43.
- TR-DECOY: 「in-void」 contains 「in」 as a substring; 库存/README.md says the status is matched exactly, a substring match gives 67327.74.
- TR-DEFN: summing every row regardless of type is far higher.

## Reference solution
1. bash: `cat 库存/2026-09/*.csv | awk -F, '$2=="in" {s+=$3} END{printf "%.2f\n", s}'`
Final answer: Total received in September: 46472.40 units (type exactly `in`; `in-void` reversals are not counted).

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all 4 files are summed.
