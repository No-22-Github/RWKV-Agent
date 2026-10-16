## Traps
- days vs weight_kg; ZTO vs YTO look alike
- fixture: ship/deliveries.csv, 600 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 ship/deliveries.csv
    awk -F',' 'NR>1 && NF && $2=="ZTO" && $4>=5{n++} END{print n+0}' ship/deliveries.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
