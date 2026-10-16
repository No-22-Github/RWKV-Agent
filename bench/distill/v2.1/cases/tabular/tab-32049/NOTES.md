## Traps
- input is tab separated, output must be comma separated
- fixture: lab/od_readings.tsv, 300 data rows, delimiter '\t'

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 lab/od_readings.tsv
    printf 'plate,mean_od600\n' > lab/plate_means.csv
    awk -F'\t' 'NR>1 && NF{s[$2]+=$3; n[$2]++} END{for(k in s) printf "%s,%.3f\n", k, s[k]/n[k]}' lab/od_readings.tsv | sort >> lab/plate_means.csv
    cat lab/plate_means.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
