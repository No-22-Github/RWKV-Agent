## Traps
- TR-MULTISRC: six monthly exports; one month alone is a plausible wrong total.
- TR-DECOY: KXL- SKUs share the KX prefix but exports/README.md says they are a different line; `grep KX` over-counts.

## Reference solution
1. bash: `cat exports/*/orders.csv | awk -F, '$3=="refunded" && $2 ~ /^KX-/ {s+=$4} END{printf "%.2f\n", s}'`
Final answer: refunds on the Kestrel (KX-) line from March to August total $7521.21; KXL- accessories are excluded per exports/README.md.

## Why the answer is unique
Status and SKU are exact fields; the README pins KX- versus KXL-.
