## Traps
- Answer: 51. TR-DECOY: including Eastgate Annex gives 105.
- TR-MULTISRC: 6 files; the first one alone gives 9.
- Data volume: 6 data files, 129 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat library/loans/*.jsonl | jq -s 'map(select(.branch=="Eastgate" and .overdue)) | length'` -> 51
Final answer: Eastgate had 51 overdue loans (Eastgate Annex not included).

## Why the answer is unique
branch is an exact string and overdue a boolean; the README separates Eastgate from Eastgate Annex.
