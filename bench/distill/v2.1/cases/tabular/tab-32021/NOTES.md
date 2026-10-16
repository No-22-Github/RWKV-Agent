## Traps
- first line is a # comment; empty lines at end
- fixture: 生产/日报.csv, 390 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 生产/日报.csv
    awk -F, 'NR>2 && NF && $2=="三车间" && $5=="晚"{s+=$3} END{print s+0}' 生产/日报.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
