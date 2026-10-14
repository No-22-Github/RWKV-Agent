## Traps
- Answer: 7326790.
- TR-MULTISRC: 5 files; the first one alone gives 1601395.
- Data volume: 5 data files, 48 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no perl, so running tools/bytes.pl fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat logs/www/*.log | awk '$4 ~ /^2/ {s+=$5} END {print s}'` -> 7326790
Final answer: bytes.pl reports 7326790 bytes (2xx responses only); perl is missing, so I reproduced it with awk.

## Why the answer is unique
The script's status filter is in its source.
