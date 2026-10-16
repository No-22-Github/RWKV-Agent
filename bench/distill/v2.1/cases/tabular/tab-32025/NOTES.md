## Traps
- 数量 and 金额 are numeric decoys; the ranking is by number of lines, not quantity
- fixture: 电商/订单行.csv, 420 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 电商/订单行.csv
    awk -F',' 'NR>1 && NF{print $2}' 电商/订单行.csv | sort | uniq -c | sort -rn | head -n 3

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
