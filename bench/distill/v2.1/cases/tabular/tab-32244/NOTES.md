## Traps
- TR-DEFN: revenue is units*price, not a plain row count or price sum.

## Reference solution
1. awk accumulate units*price per product, sort -rn, head -3, format into the file.
Reference commands (replayed in the sandbox): tail -n +2 sales/week.csv | awk -F, '{r[$1]+=$2*$3} END{for(p in r) print r[p], p}' | sort -rn | head -3 | awk '{printf "%d. %s: %d\n", NR, $2, $1}' > report/top3.txt; cat report/top3.txt; echo 3
Final answer: turn 1 -> 15259 Elm; turn 2 -> 3 

## Why the answer is unique
Distinct top three revenues.
