## Traps
- Answer: 64. TR-DECOY: prefix-matching /api/v2/orders/export too gives 87.
- TR-MULTISRC: 6 files; the first one alone gives 11.
- Data volume: 6 data files, 153 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat logs/edge/*.log | awk '$7=="/api/v2/orders" && $9 ~ /^5/' | wc -l` -> 64
Final answer: /api/v2/orders returned 64 5xx responses over 8-13 September.

## Why the answer is unique
Status and path are exact fields of each line; the README pins the endpoint, so one count results.
