## Traps
- TR-RULEFILE: the rate and the size clause both live in storage_terms.md: 2.40 pounds a cask for the quarter, and a cask of more than 300 litres counts as two casks. The fill file carries capacities only. A reader who counts every cask once answers 100.8 instead of 144.0.
- TR-DUPROW: the bonded store export was repeated and writes four of the fills out again, and the repeated rows match their originals in every column. Charging the rows rather than the casks answers 160.8 instead of 144.0.

## Reference solution
1. List the workspace: the quarter's fill file, the storage terms and a short readme.
2. Read storage_terms.md: 2.40 pounds a cask for the quarter, and a cask over 300 litres counts as two casks.
3. Read cask_fills_2026_q2.csv, count each fill_id once, work out how many casks its capacity is worth and multiply by 2.40 pounds: 144.0 pounds.

## Why the answer is unique
The capacity of each cask comes from the fill file and the rate and the size clause from the storage terms; nothing else in the workspace states a charge. The clause is written on the cask, so a capacity fixes how many casks a fill is charged for, and the repeats are the same fills written out again, so each fill_id is charged once. The charge comes to 144.0 pounds.
