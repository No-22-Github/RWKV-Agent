## Traps
- TR-DECOY: the status code 502 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (88 lines).

## Reference solution
cat app/worker.log | grep -F 'status=502 ' | grep -F ' worker - ' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 24 16:52:44; 28 16:59:19

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
