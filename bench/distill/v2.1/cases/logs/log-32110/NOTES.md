## Traps
- TR-DECOY: the status code 429 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (51 lines).

## Reference solution
cat logs/rate.log | grep -F ' status=429 ' | grep -F ' svc=api ' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 40 08:13

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
