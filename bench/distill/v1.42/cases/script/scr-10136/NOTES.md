## Traps
- Answer: 276.
- TR-MULTISRC: 5 files; the first one alone gives 50.
- Data volume: 5 data files, 79 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no node, so running scripts/rejected.js fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat data/applications/*.jsonl | jq -s 'map(select(.status=="rejected")) | length'` -> 276
Final answer: rejected.js prints 276; node is not installed, so I counted exact status=="rejected" with jq (rejected_auto excluded).

## Why the answer is unique
The script compares status for exact equality.
