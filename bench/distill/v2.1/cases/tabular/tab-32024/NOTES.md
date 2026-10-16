## Traps
- file ends with two empty lines; a naive row count divides by the wrong n
- fixture: water/samples.csv, 280 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 water/samples.csv
    awk -F',' 'NR>1 && NF && $2=="east"{s+=$3;n++} END{printf "%.2f\n", s/n}' water/samples.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
