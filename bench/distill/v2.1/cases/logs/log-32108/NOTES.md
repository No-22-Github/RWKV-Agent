## Traps
- TR-DECOY: the status code 500 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (53 lines).

## Reference solution
cat logs/ledger-app.log | grep -F 'status=500 ' | grep -F ' sync - ' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 51 08:08

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
