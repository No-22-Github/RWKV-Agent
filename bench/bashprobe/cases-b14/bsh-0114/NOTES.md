## Traps
- Answer: web.
- Data volume: 1 data files, 167 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `jq -s 'map(select(.result=="cancelled")) | group_by(.repo) | map({r: .[0].repo, n: length}) | sort_by(-.n) | .[0:3]' ci/builds.jsonl` -> web
Final answer: web.

## Why the answer is unique
branch and result are exact strings; the README separates main from main-backup.
