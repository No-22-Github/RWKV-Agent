## Traps
- Turn 1: 114.
- Turn 2: 73.
- Data volume: 1 data files, 167 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `jq -s 'map(select(.repo=="infra" and .duration_s>1200)) | length' ci/builds.jsonl` -> 114
Turn 2: bash: `jq -s 'map(select(.repo=="infra" and .duration_s>1200 and .result=="passed")) | length' ci/builds.jsonl` -> 73
Final answer (last turn): 73 of the slow infra builds passed.

## Why the answer is unique
branch and result are exact strings; the README separates main from main-backup.
