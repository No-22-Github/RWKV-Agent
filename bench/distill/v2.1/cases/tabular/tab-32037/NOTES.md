## Traps
- header 身高cm / 体重kg include units; 不及格 contains 及格
- fixture: 体测/2026春.csv, 600 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 体测/2026春.csv
    awk -F',' 'NR>1 && NF && $2=="工学院" && $3=="女" && $6=="不及格" && $4>160{n++} END{print n+0}' 体测/2026春.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
