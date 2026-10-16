## Traps
- TR-MULTISRC: the matching lines are spread over every file; any single file gives a partial count.
- TR-DECOY: status codes also occur inside durations, byte counts and paths.

## Reference solution
cat the files oldest first, filter with exact field patterns, then wc -l / sort | uniq -c | sort -rn | head.

Expected tokens per turn: 139 15:44

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
