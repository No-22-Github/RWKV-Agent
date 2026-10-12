## Traps
- Turn 1: exact answer 1167; the loose match (prefix match on service and action) gives 1369.
- Turn 2: exact answer 7; the loose match (prefix match on service and action) gives 51.
- TR-TRUNC: the file is 65KB and 1374 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.
- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.

## Reference solution
Turn 1: bash: `awk '$3=="payments" && $4=="ROLLBACK" {n=NR} END{print n}' ops/deploy-history.txt` -> 1167
Turn 2: bash: `awk '$3=="payments" && $4=="ROLLBACK"' ops/deploy-history.txt | wc -l` -> 7
Final answer: payments has 7 ROLLBACK events.

## Why the answer is unique
service and action are whole-value columns and the file has no header, so line numbers equal row numbers. The README (ops/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Total number of ROLLBACK lines for the payments service?
2. Count the payments rollbacks (not dry runs) in deploy-history.txt.
3. How many times was payments rolled back, per ops/README.md?
4. Number of lines with service payments and action ROLLBACK.
5. How many real rollbacks did the payments service have?
