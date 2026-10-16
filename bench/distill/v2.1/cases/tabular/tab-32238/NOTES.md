## Traps
- TR-DECOY: most SKUs match; only a handful differ.

## Reference solution
1. join on sku, awk compare.
Reference commands (replayed in the sandbox): join -t, <(tail -n +2 inv/system.csv | sort) <(tail -n +2 inv/stocktake.csv | sort) | awk -F, '$2!=$3{print $1; n++} END{print n}'
Final answer: turn 1 -> 6 SKU-10000 SKU-10017 SKU-10595 SKU-11210 SKU-11245 SKU-11462

## Why the answer is unique
Join by sku, compare quantities.
