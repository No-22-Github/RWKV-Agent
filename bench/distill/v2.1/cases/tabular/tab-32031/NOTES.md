## Traps
- 学院 filter must be applied before ranking
- fixture: 校园/社团报名.csv, 450 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 校园/社团报名.csv
    awk -F',' 'NR>1 && NF && $3=="工学院"{print $2}' 校园/社团报名.csv | sort | uniq -c | sort -rn | head -n 3
Turn 2:
    awk -F',' 'NR>1 && NF && $3=="文学院"{print $2}' 校园/社团报名.csv | sort | uniq -c | sort -rn | head -n 3

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
