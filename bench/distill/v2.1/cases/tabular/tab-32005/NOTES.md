## Traps
- 状态 value 逾期未还 contains 未还; grep 未还 over-counts
- fixture: 图书馆/借阅记录.csv, 340 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 图书馆/借阅记录.csv
    awk -F',' 'NR>1 && NF && $6=="未还"{n++} END{print n+0}' 图书馆/借阅记录.csv
Turn 2:
    awk -F',' 'NR>1 && NF && $6=="逾期未还"{n++} END{print n+0}' 图书馆/借阅记录.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
