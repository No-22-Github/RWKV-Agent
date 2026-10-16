## Traps
- void orders must not be counted
- fixture: sales/orders.csv, 460 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 sales/orders.csv
    printf 'customer,paid_total\n' > sales/top3_customers.csv
    awk -F, 'NR>1 && NF && $4=="paid"{s[$2]+=$3} END{for(k in s) printf "%s,%.2f\n", k, s[k]}' sales/orders.csv | sort -t, -k2,2 -rn | head -n 3 >> sales/top3_customers.csv
    cat sales/top3_customers.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
