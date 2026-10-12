## Traps
- TR-DECOY: exact answer 13690; the loose reading (prefix match on zone and valve) gives 32365.
- TR-MULTISRC: 5 files; the first file alone gives 2991.

## Reference solution
Turn 1: bash: `cat irrigation/*.txt | awk -F, '$2=="Z2" && $3=="open" {s+=$4} END{print s}'` -> 13690
Final answer: 13690 litres.

## Why the answer is unique
zone and valve are whole-value columns. The README (irrigation/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Total litres for zone Z2 where valve is open?
2. Sum the liters column for Z2 rows with valve open.
3. Per irrigation/README.md, how much water did Z2 use with the valve open?
4. Add the litres of all Z2/open records Monday to Friday.
5. What is the weekly open-valve water use of zone Z2?
