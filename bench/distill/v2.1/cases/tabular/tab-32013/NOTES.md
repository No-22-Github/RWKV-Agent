## Traps
- 商品金额 vs 退款金额 adjacent
- fixture: 销售/订单.csv, 400 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 销售/订单.csv
    awk -F',' 'NR>1 && NF && $2=="华南"{s+=$3} END{printf "%.2f\n", s}' 销售/订单.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
