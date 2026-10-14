## Traps
- Answer: /static/app.js. TR-DECOY: lumping 401s in with 404s gives /api/v2/orders.
- Data volume: 6 data files, 157 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
1. bash: `cat logs/edge/*.log | awk '$9==404 {print $7}' | sort | uniq -c | sort -rn | head -3` -> /static/app.js
Final answer: /static/app.js had the most 404s.

## Why the answer is unique
Status and path are exact fields of each line; the README pins the endpoint, so one count results.
