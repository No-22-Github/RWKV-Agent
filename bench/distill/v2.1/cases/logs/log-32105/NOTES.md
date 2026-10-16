## Traps
- TR-DECOY: the status code 429 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (57 lines).

## Reference solution
cat logs/api-0915.jsonl | grep -F '"status":429,' | grep -F '"path":"/api/items"' | grep -F '"level":"WARN"' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 56 08:02; 55 08:19

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
