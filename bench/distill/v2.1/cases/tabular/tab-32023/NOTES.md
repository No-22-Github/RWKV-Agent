## Traps
- freight vs weight_kg; 加急 is a value not a column
- fixture: 物流/运费.csv, 360 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 物流/运费.csv
    awk -F',' 'NR>1 && NF && $2=="宁波" && $5=="加急"{s+=$4} END{printf "%.2f\n", s}' 物流/运费.csv
Turn 2:
    awk -F',' 'NR>1 && NF && $2=="温州" && $5=="标准"{s+=$4;n++} END{printf "%.2f\n", s/n}' 物流/运费.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
