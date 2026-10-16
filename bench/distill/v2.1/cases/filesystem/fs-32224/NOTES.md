## Traps
- TR-TRUNC: over 150 files so a listing is cut at 50.
- TR-DECOY: the second-biggest directory is close behind.

## Reference solution
1. find archive -type f | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head.
2. Then count .pdf in that directory.
Reference commands (replayed in the sandbox): find archive -type f -name '*.pdf' | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -3
Final answer: turn 1 -> 38 archive/misc; turn 2 -> 25 

## Why the answer is unique
Direct children only; unique winner.
