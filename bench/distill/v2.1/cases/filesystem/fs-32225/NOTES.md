## Traps
- TR-TRUNC: 90 files, one listing returns 50 and has no sizes anyway.

## Reference solution
1. find -exec wc -c {} + | sort -rn | head -5.
Reference commands (replayed in the sandbox): find downloads -type f -exec wc -c {} + | grep -v ' total$' | sort -rn | head -5
Final answer: turn 1 -> 8900 report-18.pdf report-12.pdf report-80.txt notes-41.txt photo-83.pdf

## Why the answer is unique
All sizes distinct.
