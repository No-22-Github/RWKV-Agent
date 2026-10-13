## Traps
- Turn 1: 38.
- Turn 2: 9.
- TR-MULTISRC: 6 files; the first one alone gives 0.
- Data volume: 6 data files, 128 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat library/loans/*.jsonl | jq -s 'map(select(.overdue and .format=="audiobook") | .member) | unique | length'` -> 38
Turn 2: bash: `cat library/loans/*.jsonl | jq -s 'map(select(.overdue and .format=="audiobook" and .branch=="Hillcrest") | .member) | unique | length'` -> 9
Final answer (last turn): 9 members at Hillcrest.

## Why the answer is unique
branch is an exact string and overdue a boolean; the README separates Eastgate from Eastgate Annex.
