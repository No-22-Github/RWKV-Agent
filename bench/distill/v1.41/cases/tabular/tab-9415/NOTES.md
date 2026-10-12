## Traps
- TR-DECOY: exact answer 49; the loose reading (prefix match on queue and status) gives 139.
- TR-MULTISRC: 3 files; the first file alone gives 22.

## Reference solution
Turn 1: bash: `cat helpdesk/*.txt | awk -F, '$2=="billing" && $3=="closed"' | wc -l` -> 49
Final answer: 49 tickets.

## Why the answer is unique
queue and status are whole-value columns. The README (helpdesk/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Count rows with queue billing and status closed across q1 to q3.
2. Per helpdesk/README.md, how many billing tickets were closed?
3. Number of closed tickets in the billing queue (not billing-eu).
4. How many export rows have queue=billing and status=closed?
5. Total closed billing tickets over the three quarters.
