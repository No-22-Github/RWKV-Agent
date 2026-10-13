## Traps
- Answer: 119. TR-DECOY: matching main-backup gives 144.
- Data volume: 1 data files, 161 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `jq -s 'map(select(.branch=="main" and .result=="failed")) | length' ci/builds.jsonl` -> 119
Final answer: 119 failed builds on main (main-backup excluded).

## Why the answer is unique
branch and result are exact strings; the README separates main from main-backup.
