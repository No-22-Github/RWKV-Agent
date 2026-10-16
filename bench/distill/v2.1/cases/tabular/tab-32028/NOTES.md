## Traps
- note is quoted and may contain a comma; trailing empty line
- fixture: iot/heartbeat.csv, 380 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 iot/heartbeat.csv
    cat iot/heartbeat.csv | sed -E 's/"[^",]*,[^"]*"/Q/g' | awk -F, 'NR>1 && NF && $3=="1.5.0"{print $1}' | sort -u | wc -l

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
