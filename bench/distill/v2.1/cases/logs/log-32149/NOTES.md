## Traps
- TR-DECOY: planted slow requests exist on other paths too (outliers are planted only on the target path, but ordinary slow requests exist everywhere).

## Reference solution
See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.

Expected tokens per turn: r-010632 8222 r-ab357a 8155 r-a0cbff 7230

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
