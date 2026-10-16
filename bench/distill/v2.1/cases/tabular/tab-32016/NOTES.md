## Traps
- latency_ms vs bytes; status column is text of digits
- fixture: access_summary.csv, 580 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 access_summary.csv
    awk -F',' 'NR>1 && NF && $2=="/search" && $3=="200"{s+=$4;n++} END{printf "%.1f\n", s/n}' access_summary.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
