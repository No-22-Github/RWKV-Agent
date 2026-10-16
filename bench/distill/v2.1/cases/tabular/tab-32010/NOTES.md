## Traps
- subject columns 语文,数学,英语 adjacent; a guess of 数学 as column 3 is wrong
- fixture: 成绩/期中.csv, 420 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 成绩/期中.csv
    awk -F',' 'NR>1 && NF && $2=="高二(3)班" && $4>120{n++} END{print n+0}' 成绩/期中.csv
Turn 2:
    awk -F',' 'NR>1 && NF && $2=="高二(3)班" && $5>120{n++} END{print n+0}' 成绩/期中.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
