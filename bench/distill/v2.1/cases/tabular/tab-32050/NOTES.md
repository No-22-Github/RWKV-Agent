## Traps
- 预算 and 实际 both quoted with thousands commas; difference = actual minus budget
- fixture: 预算/执行.csv, 280 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 预算/执行.csv
    printf '科目,预算合计,实际合计,差额\n' > 预算/科目对比.csv
    cat 预算/执行.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F, 'NR>1 && NF{b[$3]+=$4; a[$3]+=$5} END{for(k in b) printf "%s,%.2f,%.2f,%.2f\n", k, b[k], a[k], a[k]-b[k]}' | sort >> 预算/科目对比.csv
    cat 预算/科目对比.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
