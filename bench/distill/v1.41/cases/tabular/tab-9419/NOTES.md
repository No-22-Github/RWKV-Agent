## Traps
- TR-DECOY: exact answer 904; the loose reading (prefix match on unit and state) gives 114.
- TR-MULTISRC: 3 files; the first file alone gives 1048.

## Reference solution
Turn 1: bash: `cat solar/*.dat | awk -F';' '$2=="INV-3" && $3=="grid" {print $4}' | sort -n | head -1` -> 904
Final answer: 904 W.

## Why the answer is unique
unit and state are whole-value columns. The README (solar/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Minimum watts for INV-3 with state grid?
2. Lowest output of INV-3 while feeding the grid.
3. Per solar/README.md, what is INV-3's smallest watts reading in state grid?
4. Smallest watts value among INV-3/grid samples.
5. How low did INV-3 go while in grid state across the three days?
