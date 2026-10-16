## Traps
- month filter ≥ 07 over a date column; fractional days; one trailing empty line
- fixture: 人事/请假.csv, 360 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 人事/请假.csv
    awk -F',' 'NR>1 && NF && $3=="研发" && $4=="病假" && $6>="2026-07-01"{s+=$5} END{printf "%.1f\n", s}' 人事/请假.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
