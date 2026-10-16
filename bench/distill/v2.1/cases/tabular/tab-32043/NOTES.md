## Traps
- 订单金额 vs 退款金额 adjacent; output must be sorted by total, descending
- fixture: 报表/订单.csv, 450 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 报表/订单.csv
    printf '区域,订单数,订单金额合计\n' > 报表/区域汇总.csv
    awk -F, 'NR>1 && NF{n[$2]++; s[$2]+=$4} END{for(k in n) printf "%s,%d,%.2f\n", k, n[k], s[k]}' 报表/订单.csv | sort -t, -k3,3 -rn >> 报表/区域汇总.csv
    cat 报表/区域汇总.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
