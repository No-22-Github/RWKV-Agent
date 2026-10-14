## Traps
- Answer: 60.
- Data volume: 1 data files, 160 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `jq -s 'map(select(.repo=="worker" and .result=="failed") | .tests_failed) | add' ci/builds.jsonl` -> 60
Final answer: 60 failed tests across failed worker builds.

## Why the answer is unique
branch and result are exact strings; the README separates main from main-backup.
