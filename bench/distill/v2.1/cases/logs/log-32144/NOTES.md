## Traps
- TR-DECOY: the bytes column is larger than rt; rt=4.231 means seconds.

## Reference solution
See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.

Expected tokens per turn: r-f425f5 r-ad6145 r-dde30f

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
