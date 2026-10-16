## Traps
- copies vs row count give different rankings
- fixture: library/catalog.csv, 270 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 library/catalog.csv
    awk -F',' 'NR>1 && NF{s[$2]+=$4} END{for(k in s) printf "%.2f %s\n", s[k], k}' library/catalog.csv | sort -rn | head -n 3

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
