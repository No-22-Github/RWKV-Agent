## Traps
- 实付金额/退款金额 adjacent columns; 状态 is column 6, not 5
- fixture: data/订单明细.csv, 380 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 data/订单明细.csv
    awk -F, -v c=6 'NR>1 && $c=="已退款"{n++} END{print n+0}' data/订单明细.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
