## Traps
- TR-DECOY: OOM appears three times; the question is about the first, and WARN lines continue after it.

## Reference solution
See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.

Expected tokens per turn: r-a229ad 13:30 r-d7740e

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
