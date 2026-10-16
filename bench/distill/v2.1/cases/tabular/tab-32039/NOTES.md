## Traps
- origin and dest use the same codes; PVG->PEK differs from PEK->PVG
- fixture: air/flights.csv, 438 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 air/flights.csv
    awk -F',' 'NR>1 && NF && $3=="PVG" && $4=="PEK" && $5>60{n++} END{print n+0}' air/flights.csv
Turn 2:
    awk -F',' 'NR>1 && NF && $3=="PVG" && $4=="PEK" && $5>60{s+=$6} END{print s+0}' air/flights.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
