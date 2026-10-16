## Traps
- amount quoted with thousands commas; months derived from a date
- fixture: ledger/entries.csv, 400 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 ledger/entries.csv
    printf 'month,total\n' > ledger/monthly_totals.csv
    cat ledger/entries.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F, 'NR>1 && NF{s[substr($2,1,7)]+=$4} END{for(k in s) printf "%s,%.2f\n", k, s[k]}' | sort >> ledger/monthly_totals.csv
    cat ledger/monthly_totals.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
