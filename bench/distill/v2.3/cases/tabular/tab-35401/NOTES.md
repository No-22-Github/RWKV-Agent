## Traps
- TR-DECOY: the tool the task naturally needs is not in this catalog (never_offer: calculator).

## Reference solution
bash: awk -F, 'NR>1{s+=$3*$4} END{printf "%.2f\n", s*1.0825}' billing/inv-halden-0924.csv -> 2183.51

## Why the answer is unique
14 lines, qty*unit_price summed, times 1.0825. The answer is recomputed from the fixture in verify.py.

Expected: 2183.51 | 2,183.51
