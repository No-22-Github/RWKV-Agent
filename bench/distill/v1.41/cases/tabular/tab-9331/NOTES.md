## Traps
- TR-DECOY: exact answer Elena; the loose reading (type prefix match, includes BILL-WAIVED) gives Aiko.
- TR-MULTISRC: 3 files; the first file alone gives Hugo.

## Reference solution
Turn 1: bash: `cat timesheets/*.txt | awk -F, '$3=="BILL" {s[$2]+=$4} END{for (k in s) print s[k], k}' | sort -rn | head -1` -> Elena
        the same pipeline prints the total (120) next to the name
Final answer: Elena logged the most billable hours (120).

## Why the answer is unique
type is a whole-value column; the leader is ahead by at least six hours. The README (timesheets/README.md) fixes the rule; the answer is a single name.

## Five alternative phrasings of the task
1. Who has the highest total of BILL hours in timesheets/?
2. Name the engineer with the largest billable-hours total, per the README.
3. Across January to March, which engineer billed the most hours?
4. Top engineer by hours where type is exactly BILL.
5. Which person leads on billable hours (written-off time excluded)?
