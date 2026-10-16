## Traps
- TR-DECOY: the status code 404 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (0 lines).

## Reference solution
cat logs/session-edge.log | grep -F ' status=404 ' | grep -F ' svc=session ' | grep -F ' level=warn ' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 48 16:44:42

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
