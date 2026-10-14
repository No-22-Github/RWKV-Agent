## Traps
- Answer: Eastgate Annex.
- Data volume: 6 data files, 131 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat library/loans/*.jsonl | jq -s 'map(select(.overdue)) | group_by(.branch) | map({b: .[0].branch, n: length}) | sort_by(-.n) | .[0:3]'` -> Eastgate Annex
Final answer: Eastgate Annex had the most overdue loans.

## Why the answer is unique
branch is an exact string and overdue a boolean; the README separates Eastgate from Eastgate Annex.
