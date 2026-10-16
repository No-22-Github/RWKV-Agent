## Traps
- TR-DECOY: status codes are also three-digit numbers; only took=..ms is the duration.

## Reference solution
See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.

Expected tokens per turn: r-73fdef 8452 r-938eb3 6758

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
