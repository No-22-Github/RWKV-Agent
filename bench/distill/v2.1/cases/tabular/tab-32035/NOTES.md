## Traps
- month lives inside a date column; 退款状态 has 部分退款 and 已退款
- fixture: 电商/订单_q3.csv, 600 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 电商/订单_q3.csv
    awk -F',' 'NR>1 && NF && $2=="华东" && substr($3,1,7)=="2026-09" && $5=="已退款"{n++} END{print n+0}' 电商/订单_q3.csv
Turn 2:
    awk -F',' 'NR>1 && NF && $2=="华东" && substr($3,1,7)=="2026-09" && $5=="已退款"{s+=$4} END{printf "%.2f\n", s}' 电商/订单_q3.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
