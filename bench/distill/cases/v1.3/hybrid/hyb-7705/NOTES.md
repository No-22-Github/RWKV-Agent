## Traps
- TR-NEARNAME: the request names deliveries-sept.csv, a name that no longer exists. The
  workspace holds deliveries-2026-09.csv (the monthly export, 101 bags) and a stale snapshot
  deliveries-sept.csv.bak whose September rows total 36. The README pins the monthly naming
  scheme and marks .bak snapshots as stale and partial.

## Reference solution
1. list_files: deliveries-2026-09.csv and deliveries-sept.csv.bak sit at the top level next to README.md.
2. read_file README.md: monthly exports are deliveries-YYYY-MM.csv; .bak snapshots are stale and partial.
3. read_file deliveries-2026-09.csv. Turn 1: 101 bags. Turn 2: dropping the two Fernhall market run rows (5 + 4) gives 92. Turn 3: the biggest single delivery is Stonebridge Mills, 18 bags on 2 September.

## Why the answer is unique
The stale snapshot carries only two September rows (17 + 19 = 36) and its top rows are June-dated, so it cannot answer a September total under the README's naming policy; the monthly file is the only complete September record. Within it, the market-run rows are named as such, so 101 then 92 are the only readings, and 18 is the single largest delivery.

## Five alternative phrasings of the task
1. fernhall bakehouse september flour deliveries
2. how many bags of flour arrived in september
3. kitchen flour total without the market runs
4. which supplier made the largest september delivery
5. september delivery sheet bags by supplier
