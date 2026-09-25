## Traps
- TR-AMBIG: the first request names "the Marchwold yard" while the register holds two
  yards called Marchwold, one at Thornwell and one at Marple. Thornwell's rows give 155
  (46 + 52 + 57); Marple's three rows give 114. The register alone cannot say which yard
  the pallet pool means, so the assistant has to ask before it adds anything up.

## Reference solution
1. list_files: the workspace holds movements/september-2026.csv and README.md.
2. read_file movements/september-2026.csv: the yard column names two Marchwold yards, so
   the request is not yet settled and the assistant asks which one is meant.
3. Turn 2 fixes the Thornwell yard. Add that yard's rows: 46 + 52 + 57 = 155.

## Why the answer is unique
After the clarification only one of the two Marchwold yards is in scope. The register
records each day's movement as its own row under one yard, and no row is repeated, so
the Thornwell yard's September pallets are its three rows: 46 on 3 September, 52 on 12
September and 57 on 23 September, giving 155. The decoy 114 is the Marple yard's three
rows; it is a real figure, but it answers a different yard, and the request was settled
on Thornwell before the sum was taken.

## Five alternative phrasings of the task
1. thornwell haulage marchwold yard pallets september
2. how many pallets left the marchwold yard in september
3. thornwell haulage pallet movements by yard
4. marchwold yard thornwell and marple pallet totals
5. thornwell haulage september pallet register
