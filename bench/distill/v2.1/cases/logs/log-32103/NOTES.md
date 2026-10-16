## Traps
- TR-DECOY: the status code 500 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (0 lines).

## Reference solution
cat var/log/shop/edge.log | grep -F ' status=500 ' | grep -F ' path=/shop/buy ' | grep -F ' level=error ' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 49 08:12

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
