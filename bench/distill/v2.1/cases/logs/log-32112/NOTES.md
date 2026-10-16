## Traps
- TR-DECOY: the status code 503 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (26 lines).

## Reference solution
cat logs/gateway-app.log | grep -F 'status=503 ' | grep -F ' gateway - ' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 20 08:09; 16 09:05

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
