## Traps
- TR-DECOY: the status code 500 also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (22 lines).

## Reference solution
cat www/log/access.log | grep -F 'HTTP/1.1" 500 ' | grep -F ' /v2/invoices HTTP' | wc -l  (exact field patterns, one grep per condition).

Expected tokens per turn: 15 15:51:34; 18 16:39:10

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
