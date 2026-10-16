## Traps
- 摘要 may be quoted with comma
- 金额 may be quoted with thousands comma; two sed passes needed
- fixture: 财务/报销.csv, 330 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 财务/报销.csv
    cat 财务/报销.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed -E 's/"[^",]*,[^"]*"/Q/g' | sed 's/"//g' | awk -F, 'NR>1 && NF && $3=="招待"{s+=$5} END{printf "%.2f\n", s}'

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
