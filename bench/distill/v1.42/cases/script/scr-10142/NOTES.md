## Traps
- Answer: 242.
- TR-MULTISRC: 7 files; the first one alone gives 37.
- Data volume: 7 data files, 50 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no sqlite3, so running queries/paid_pro.sql fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat data/signups/*.csv | awk -F, '$2=="pro" && $4=="no"' | wc -l` -> 242
Final answer: The query returns 242; sqlite3 is not available, so I counted the same rows with awk.

## Why the answer is unique
The SQL filter is explicit in the script.
