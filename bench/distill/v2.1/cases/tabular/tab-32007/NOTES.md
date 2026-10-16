## Traps
- order_total like "12,345.60" is quoted; naive awk reads 12 and shifts later columns
- fixture: sales/orders_h2.csv, 280 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 sales/orders_h2.csv
    cat sales/orders_h2.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F, 'NR>1 && NF && $3>10000{n++} END{print n+0}'

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
