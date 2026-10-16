## Traps
- TR-DECOY: the status code 404 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (30 lines).

## Reference solution
cat logs/access.log | grep -F 'HTTP/1.1" 404 ' | grep -F ' /api/cart HTTP' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 24 08:04:39; 25 08:30:00

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
