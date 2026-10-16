## Traps
- TR-DECOY: ERROR lines also occur before the marker; only the first one after it counts.

## Reference solution
See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.

Expected tokens per turn: r-aeabc8 12:02:08 r-fe8815 12:04:46

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
