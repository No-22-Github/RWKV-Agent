## Traps
- TR-TRUNC: ~90 files so a listing is cut at 50.

## Reference solution
1. find -name '*.log' -exec wc -c; awk to path,bytes; sort; prepend header.
Reference commands (replayed in the sandbox): find logs -type f -name '*.log' -exec wc -c {} + | grep -v ' total$' | awk '{print $2","$1}' | sort > /tmp/rows.txt; (echo path,bytes; cat /tmp/rows.txt) > logs/index.csv; wc -l < /tmp/rows.txt; cat logs/index.csv
Final answer: turn 1 -> 40 

## Why the answer is unique
Byte sizes and sorted paths are determined.
