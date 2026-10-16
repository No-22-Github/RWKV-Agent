## Traps
- 数量 uses thousands separators and is quoted; 单价 follows it
- fixture: 采购/订单.csv, 600 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -4 采购/订单.csv
    cat 采购/订单.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F',' 'NR>1 && NF && $3=="轴承" && $4>3000 && $6=="延期"{n++} END{print n+0}'
Turn 2:
    cat 采购/订单.csv | sed -E ':a;s/"([0-9]+),([0-9]{3})/"\1\2/;ta' | sed 's/"//g' | awk -F',' 'NR>1 && NF && $3=="轴承" && $4>3000 && $6=="延期" && $2=="恒达"{n++} END{print n+0}'

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
