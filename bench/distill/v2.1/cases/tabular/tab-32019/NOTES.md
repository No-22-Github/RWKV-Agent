## Traps
- 总分 is a derived column next to the subjects
- fixture: 教务/月考.csv, 210 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 教务/月考.csv
    awk -F',' 'NR>1 && NF && $2=="初三2班"{s+=$4;n++} END{printf "%.1f\n", s/n}' 教务/月考.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
