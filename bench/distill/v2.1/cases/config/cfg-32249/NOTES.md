## Traps
- TR-TRUNC: ~100 files.

## Reference solution
1. jq -rs select timeout_ms>1000, names sorted, write; wc -l.
Reference commands (replayed in the sandbox): jq -rs 'map(select(.timeout_ms>1000)|.name)|sort|.[]' 配置/w*.json > 配置/slow.txt; wc -l < 配置/slow.txt; cat 配置/slow.txt
Final answer: turn 1 -> 29 ; turn 2 -> 29 

## Why the answer is unique
Strict greater than 1000.
