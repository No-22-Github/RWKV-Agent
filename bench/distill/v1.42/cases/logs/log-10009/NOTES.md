## Traps
- Turn 1: 94.
- Turn 2: 11.
- TR-MULTISRC: 6 files; the first one alone gives 3.
- Data volume: 6 data files, 157 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.

## Reference solution
Turn 1: bash: `cat logs/edge/*.log | awk '$9==401 {print $1}' | sort -u | wc -l` -> 94
Turn 2: bash: `cat logs/edge/*.log | awk '$9==401 && $7=="/login" {print $1}' | sort -u | wc -l` -> 11
Final answer (last turn): 11 distinct IPs got a 401 on /login.

## Why the answer is unique
Status and path are exact fields of each line; the README pins the endpoint, so one count results.
