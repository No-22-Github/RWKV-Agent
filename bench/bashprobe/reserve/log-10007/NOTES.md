## Traps
- Answer: 1211425. TR-DECOY: summing every status gives 1674734.
- TR-MULTISRC: 6 files; the first one alone gives 169263.
- Data volume: 6 data files, 154 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat logs/edge/*.log | awk '$7=="/static/app.js" && $9==200 {s+=$10} END {print s}'` -> 1211425
Final answer: 1211425 bytes in total for /static/app.js (status 200 only).

## Why the answer is unique
Status and path are exact fields of each line; the README pins the endpoint, so one count results.
