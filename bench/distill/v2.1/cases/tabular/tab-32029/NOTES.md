## Traps
- header names contain spaces (Sales Rep, Order ID)
- fixture: crm/closed_deals.csv, 350 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 crm/closed_deals.csv
    awk -F',' 'NR>1 && NF{print $2}' crm/closed_deals.csv | sort | uniq -c | sort -rn | head -n 2

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
