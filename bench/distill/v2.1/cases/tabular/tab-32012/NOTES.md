## Traps
- 积分 like "12,345" quoted with comma
- fixture: crm/会员.csv, 360 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 crm/会员.csv
    cat crm/会员.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F, 'NR>1 && NF && $3>5000{n++} END{print n+0}'
Turn 2:
    cat crm/会员.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F, 'NR>1 && NF && $3>5000 && $4=="白金"{n++} END{print n+0}'

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
