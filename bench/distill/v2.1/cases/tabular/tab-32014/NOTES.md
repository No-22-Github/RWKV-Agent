## Traps
- quoted numbers like "12,500" break naive column splitting; base_salary vs bonus
- fixture: hr/salaries.csv, 240 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 hr/salaries.csv
    cat hr/salaries.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F',' 'NR>1 && NF && $2=="sales"{s+=$3;n++} END{printf "%.2f\n", s/n}'

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
