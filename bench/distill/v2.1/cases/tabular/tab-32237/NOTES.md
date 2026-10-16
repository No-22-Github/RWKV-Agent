## Traps
- TR-DECOY: shipment-only orders are not amount mismatches.

## Reference solution
1. jq -r '[.order,.billed]|@csv' joined with orders.csv via join, compare amounts.
2. comm -13 for shipment-only.
Reference commands (replayed in the sandbox): jq -r .order sales/shipments.jsonl | sort > /tmp/s.txt; tail -n +2 sales/orders.csv | cut -d, -f1 | sort > /tmp/o.txt; comm -13 /tmp/o.txt /tmp/s.txt > /tmp/x.txt; cat /tmp/x.txt; wc -l < /tmp/x.txt
Final answer: turn 1 -> 8 SO100249 SO100684 SO100798 SO100861 SO101099 SO101280 SO101306 SO101325; turn 2 -> 7 SO100269 SO100371 SO100558 SO100594 SO100864 SO100968 SO101410

## Why the answer is unique
Mismatches only among common ids.
