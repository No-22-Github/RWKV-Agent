## Traps
- TR-DECOY: exact answer 16536; the loose match (prefix match, includes DHL-Freight) gives 23560.
- TR-MULTISRC: 4 files; the first file alone gives 3665.

## Reference solution
Turn 1: bash: `cat freight/*.dat | awk -F';' '$2=="DHL" {s+=$3} END{print s}'` -> 16536
Final answer: DHL shipped 16536 kg in total.

## Why the answer is unique
carrier is a whole-value column. The README (freight/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Sum the kg of DHL shipments over October.
2. How many kilograms did DHL carry across the four weekly files?
3. Total kg for carrier DHL (not DHL-Freight) in freight/.
4. October weigh-ins: what is DHL's total weight in kg?
5. Add up the kg column for rows whose carrier is DHL.
