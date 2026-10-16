## Traps
- line 1 is a comment, the real header is line 2; file ends with empty lines
- fixture: 监控/温度采样.csv, 420 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 监控/温度采样.csv
    awk -F',' 'NR>2 && NF && $5=="高温"{n++} END{print n+0}' 监控/温度采样.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
