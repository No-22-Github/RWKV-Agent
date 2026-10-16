## Traps
- empty lines at end of file
- fixture: 停车/入场记录.csv, 480 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 停车/入场记录.csv
    awk -F, 'NR>1 && NF && $5=="地下一层"{print $2}' 停车/入场记录.csv | sort -u | wc -l

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
