## Traps
- TR-DECOY: the status code 401 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (43 lines).

## Reference solution
cat data/edge-0915.jsonl | grep -F '"status":401,' | grep -F '"path":"/oauth/refresh"' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 32 08:29; 20 08:01

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
