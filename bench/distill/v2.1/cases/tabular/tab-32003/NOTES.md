## Traps
- 入职地点 is quoted and contains a comma, shifting naive awk columns after it
- fixture: hr/考勤月报.csv, 300 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 hr/考勤月报.csv
    sed -E 's/"[^",]*,[^"]*"/Q/g' hr/考勤月报.csv | awk -F, 'NR>1 && $6=="2026-09" && $5>=5{n++} END{print n+0}'

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
