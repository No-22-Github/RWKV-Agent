## Traps
- plan column holds free as well; 'paying' means not free
- fixture: users.csv, 600 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 users.csv
    awk -F',' 'NR>1 && NF && $3=="pro" && $5=="yes"{n++} END{print n+0}' users.csv
Turn 2:
    awk -F',' 'NR>1 && NF && $3=="team" && $5=="yes"{n++} END{print n+0}' users.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
