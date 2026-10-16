## Traps
- TR-DECOY: ERROR/WARN lines occur before the marker too.

## Reference solution
See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.

Expected tokens per turn: r-2330c7 11:28 r-0fde80 11:58; r-2330c7 11:28 r-09ea7a 11:31

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
