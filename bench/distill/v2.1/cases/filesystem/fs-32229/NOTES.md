## Traps
- TR-DECOY: archive csv files add bytes.
- TR-TRUNC: ~100 files.

## Reference solution
1. find -name '*.csv' -not -path '*/archive/*' -exec cat {} + | wc -c.
Reference commands (replayed in the sandbox): find data -type f -name '*.csv' -not -path '*/archive/*' -exec cat {} + | wc -c
Final answer: turn 1 -> 11553 

## Why the answer is unique
Byte counts of exact files.
