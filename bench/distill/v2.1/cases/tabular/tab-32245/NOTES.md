## Traps
- TR-DUPROW: one row per event, so users repeat.

## Reference solution
1. jq -r users of purchases | sort | uniq -c | awk filter >=4, write.
Reference commands (replayed in the sandbox): jq -r 'select(.event=="purchase")|.user' 埋点/log.jsonl | sort | uniq -c | awk '$1>=4{print $2}' | sort > 埋点/heavy_users.txt; wc -l < 埋点/heavy_users.txt; cat 埋点/heavy_users.txt
Final answer: turn 1 -> 14 

## Why the answer is unique
Threshold inclusive, ids sorted.
