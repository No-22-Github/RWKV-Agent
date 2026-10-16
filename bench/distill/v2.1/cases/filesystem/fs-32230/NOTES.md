## Traps
- TR-DECOY: db logs also exceed 1000 bytes.
- TR-TRUNC: 60 files.

## Reference solution
1. find -name 'app-*.log' -size +1000c | wc -l.
2. wc -c sort -rn.
Reference commands (replayed in the sandbox): find logs -name 'app-*.log' -exec wc -c {} + | grep -v ' total$' | sort -rn | head -3
Final answer: turn 1 -> 24 ; turn 2 -> 4885 app-2026-09-10.log

## Why the answer is unique
Distinct maximum.
