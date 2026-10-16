## Traps
- reason has a two word value 'disk full' (awk default splitting breaks it); killed jobs also have reasons but must be excluded
- fixture: cluster/jobs.csv, 410 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 cluster/jobs.csv
    head -1 cluster/jobs.csv > cluster/failed_jobs.csv
    awk -F, 'NR>1 && NF && $3=="failed"' cluster/jobs.csv >> cluster/failed_jobs.csv
    wc -l cluster/failed_jobs.csv
Turn 2:
    printf 'reason,jobs\n' > cluster/failed_by_reason.csv
    awk -F, 'NR>1 && NF && $3=="failed"{print $4}' cluster/jobs.csv | sort | uniq -c | sort -rn | awk '{n=$1; $1=""; sub(/^ /,""); print $0","n}' >> cluster/failed_by_reason.csv
    cat cluster/failed_by_reason.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
