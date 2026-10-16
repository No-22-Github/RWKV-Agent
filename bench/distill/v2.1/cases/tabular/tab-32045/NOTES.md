## Traps
- first output keeps the original header and columns; second turn aggregates
- fixture: 数据/订单.csv, 380 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 数据/订单.csv
    head -1 数据/订单.csv > 数据/退款明细.csv
    awk -F, 'NR>1 && NF && $5=="退款"' 数据/订单.csv >> 数据/退款明细.csv
    wc -l 数据/退款明细.csv
Turn 2:
    printf '区域,退款单数,退款金额\n' > 数据/退款按区域.csv
    awk -F, 'NR>1 && NF && $5=="退款"{n[$2]++; s[$2]+=$4} END{for(k in n) printf "%s,%d,%.2f\n", k, n[k], s[k]}' 数据/订单.csv | sort -t, -k3,3 -rn >> 数据/退款按区域.csv
    cat 数据/退款按区域.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
