## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: data_query).

## Reference solution
bash: awk -F, 'NR>1{a[$2]+=$4} END{for(k in a) print k, a[k]}' ... -> pick the max (Westbrook, 595960); turn 2 divides by 6.

## Why the answer is unique
30 rows, 5 regions x 6 months; revenue summed per region in verify.py. Turn 2 depends on turn 1's region.

Expected: 595960 | 595,960 | Westbrook | 99327 | 99,327
