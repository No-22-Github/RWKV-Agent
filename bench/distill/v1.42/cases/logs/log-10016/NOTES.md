## Traps
- Answer: 976. TR-DECOY: summing DVDs from every branch gives 4878.
- TR-MULTISRC: 6 files; the first one alone gives 285.
- Data volume: 6 data files, 130 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat library/loans/*.jsonl | jq -s 'map(select(.format=="dvd" and .branch=="Riverside") | .days) | add'` -> 976
Final answer: 976 loan days for Riverside DVDs.

## Why the answer is unique
branch is an exact string and overdue a boolean; the README separates Eastgate from Eastgate Annex.
