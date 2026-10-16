## Traps
- impressions quoted with thousands comma shifts clicks and spend
- fixture: ads/daily.csv, 310 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 ads/daily.csv
    cat ads/daily.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F',' 'NR>1 && NF && $1=="summer_b"{s+=$5;n++} END{printf "%.2f\n", s/n}'

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
