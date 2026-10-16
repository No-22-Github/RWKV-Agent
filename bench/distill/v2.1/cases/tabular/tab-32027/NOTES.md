## Traps
- 访问ID vs 用户; counting rows instead of different users over-counts
- fixture: 埋点/访问.csv, 540 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 埋点/访问.csv
    awk -F, 'NR>1 && NF && $3=="结算"{print $2}' 埋点/访问.csv | sort -u | wc -l
Turn 2:
    awk -F, 'NR>1 && NF && $3=="购物车"{print $2}' 埋点/访问.csv | sort -u | wc -l

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
