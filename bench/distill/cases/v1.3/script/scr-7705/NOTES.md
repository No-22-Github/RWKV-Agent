## Traps
- TR-DUPROW: crossings/2026-09.csv carries GW-2203 and GW-2206 twice each (the gate system's sync retries, each re-posted row identical to its original). Summing rows instead of charges gives 25 passengers / 19100 pence instead of the billed 18 / 14200.

## Reference solution
1. Read tickets.py: its docstring fixes the layout and the one-charge-once rule.
2. Read crossings/2026-09.csv to confirm the columns and the repeated charges.
3. Write tickets.py: sweep every crossings/*.csv, keep one row per charge_id, aggregate passengers and pence per route, print in alphabetical order, then the TOTAL line.

## Why the answer is unique
With each charge counted once the merged exports (the scoring run adds crossings/2026-10.csv, which repeats GW-2303) print exactly East Sand,10,7000 / Mill Quay,7,4900 / West Head,10,9000 and TOTAL,27,20900. The docstring inside tickets.py pins the layout, and the README states the retries keep their charge_id and a charge is billed once, so the row sums (25 / 19100 in September alone) are the readings of a record the gate system itself calls re-posted; there is no reading in which GW-2203 twice is two charges.
