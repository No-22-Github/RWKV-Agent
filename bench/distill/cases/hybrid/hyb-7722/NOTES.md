## Traps
- TR-DUPROW: metrics/incidents-2026-09.csv repeats I-411 and I-414 (both staging) as extra
  identical rows. Rows number 24; distinct incidents are 22, of which 17 are production.

## Reference solution
1. read_file README.md: two staging incidents appear as an extra identical row each.
2. read_file metrics/incidents-2026-09.csv. Turn 1: 24 rows, 22 distinct incidents. Turn 2: the production subset holds 17. Turn 3: auth-gateway tops production with 7.

## Why the answer is unique
The repeated rows duplicate I-411 and I-414 field for field, so the raw 24 double-counts two incidents and the distinct count is 22. The production rows are exactly those with env=production, giving 17, and auth-gateway's seven leads billing-sync's five, so 22, 17 and auth-gateway are the only readings.

## Five alternative phrasings of the task
1. copperbeech hosting september incident register
2. incident count for september
3. production-only incident count
4. which component led production incidents
5. september incidents by environment and component
