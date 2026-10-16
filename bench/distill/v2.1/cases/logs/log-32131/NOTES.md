## Traps
- TR-DECOY: the ranking changes when the filter is dropped or applied as a substring; only exact field filters give the stated ranking.

## Reference solution
cat file | exact-field greps | extract the grouped field | sort | uniq -c | sort -rn | head -n N.

Expected tokens per turn: api 36 worker 16

## Why the answer is unique
The answer is recomputed from the fixture by verify.py with an independent line parser; the bash reference is replayed in the just-bash sidecar at build time and prints the same values.
