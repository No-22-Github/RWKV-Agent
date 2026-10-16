## Traps
- one user appears in many rows; must count users once per city, not rows
- fixture: 运营/活跃.csv, 520 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 运营/活跃.csv
    printf '城市,不同用户数\n' > 运营/城市活跃用户.csv
    awk -F, 'NR>1 && NF{print $2","$3}' 运营/活跃.csv | sort -u | cut -d, -f1 | uniq -c | awk '{print $2","$1}' | sort -t, -k2,2 -rn >> 运营/城市活跃用户.csv
    cat 运营/城市活跃用户.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
