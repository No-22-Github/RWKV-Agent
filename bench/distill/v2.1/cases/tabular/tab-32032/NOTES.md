## Traps
- amount_usd quoted with thousands commas
- fixture: procure/po_lines.csv, 330 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 procure/po_lines.csv
    cat procure/po_lines.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F',' 'NR>1 && NF{s[$2]+=$3} END{for(k in s) printf "%.2f %s\n", s[k], k}' | sort -rn | head -n 3
Turn 2:
    cat procure/po_lines.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F',' 'NR>1 && NF && $5=="Y"{s[$2]+=$3} END{for(k in s) printf "%.2f %s\n", s[k], k}' | sort -rn | head -n 3

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
