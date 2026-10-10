## Traps
- TR-NEARNAME (recovery case; the recovery behaviour is the test point): the prompt uses the business phrase "recovered, meaning restored to working order and resold", and the ledger has no column named recovered or units_recovered - the adjacent near-name pair is recovered_units versus recycled_units. Aggregating a guessed column name first fails with `field "..." is missing` (a wrong column in filter returns matched_rows 0). The model must recover: list the real columns with a data_query select (no operation), or peek at the header with at most one read_file inside the case budget, then re-query with recovered_units. The README pins the split: recovered_units go to the resale channel, recycled_units are scrapped.
- Treating the scrapped count as recovered gives 39; the correct answer is the recovered_units total, 148.

## Reference solution
1. Read README.md: recovered_units counts devices restored and resold; recycled_units counts devices scrapped for material.
2. Aggregate: {{"path":"intake/lots_2026.csv","filter":{{"device_class":"Laptop","intake_month":"2026-10"}},"operation":"sum","field":"recovered_units"}} gives 148. (If the first attempt used a guessed column name and failed, list the columns with a select query, then re-run this query.)
3. Reply with the number 148 only.

## Why the answer is unique
The decoy 39 counts scrapped devices, but the task defines recovered as restored and resold, and the README states scrapped devices never reach the resale channel, so that reading does not hold. Other device classes and months fail the filter. The answer is 148.
