## Traps
- or-condition on priority combined with and-conditions
- fixture: support/tickets.csv, 480 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 support/tickets.csv
    awk -F',' 'NR>1 && NF && $2=="tech" && ($3=="high" || $3=="urgent") && $5>48{n++} END{print n+0}' support/tickets.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
