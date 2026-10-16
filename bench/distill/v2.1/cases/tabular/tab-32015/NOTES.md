## Traps
- 销售额 vs 客单数: both numeric, order 销售额 first
- fixture: 门店/日销售.csv, 360 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 门店/日销售.csv
    awk -F',' 'NR>1 && NF && $2=="浦东店" && $3=="甜点"{s+=$4} END{printf "%.2f\n", s}' 门店/日销售.csv
Turn 2:
    awk -F',' 'NR>1 && NF && $2=="闵行店" && $3=="轻食"{s+=$4} END{printf "%.2f\n", s}' 门店/日销售.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
