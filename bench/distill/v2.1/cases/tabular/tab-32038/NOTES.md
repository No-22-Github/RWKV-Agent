## Traps
- dates are MM/DD/YYYY so the month is the first field
- total can be quoted with thousands comma
- fixture: pos/receipts.csv, 440 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 pos/receipts.csv
    cat pos/receipts.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F',' 'NR>1 && NF && substr($2,1,2)=="08" && $5=="app" && $6=="coupon"{s+=$4} END{printf "%.2f\n", s}'

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
