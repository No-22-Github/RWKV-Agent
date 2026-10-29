## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: calculator).

## Reference solution
bash: awk -F, '$2=="TRK-07"{c+=$4;l+=$3} END{printf "%.2f %.2f\n", c, c/l}' fleet/fuel-log-q3.csv -> 882.87 1.77

## Why the answer is unique
Filter one vehicle, sum cost, then cost/liters; the second turn needs the liters column as well.

Expected: 882.87 | 1.77
