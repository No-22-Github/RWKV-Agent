## Traps
- file is tab separated; awk -F, finds one column
- fixture: logs/taxi_trips.tsv, 450 data rows, delimiter '\t'

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 logs/taxi_trips.tsv
    awk -F'\t' 'NR>1 && NF && $5=="card" && $6>0{n++} END{print n+0}' logs/taxi_trips.tsv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
