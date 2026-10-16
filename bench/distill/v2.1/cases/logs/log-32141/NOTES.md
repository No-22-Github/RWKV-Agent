## Traps
- TR-DECOY: bytes and status fields also hold big numbers; only dur_ms ranks speed.

## Reference solution
See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.

Expected tokens per turn: r-75679c 7182 r-3fee15 6459 r-ce4665 6431

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
