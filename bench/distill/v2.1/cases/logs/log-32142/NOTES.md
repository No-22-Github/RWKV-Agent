## Traps
- TR-DECOY: the second turn filters by method; the overall slowest may be a GET.

## Reference solution
See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.

Expected tokens per turn: r-ab84b3 8136 r-bfa933 7970 r-fe1981 5648; r-bfa933 7970 r-9ec947 4617

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
