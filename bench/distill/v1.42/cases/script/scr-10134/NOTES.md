## Traps
- Answer: 205.
- TR-MULTISRC: 4 files; the first one alone gives 67.
- Data volume: 4 data files, 26 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no python3, so running scripts/buyers.py fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat data/activity/*.csv | awk -F, '$3=="purchase" {print $1}' | sort -u | wc -l` -> 205
Final answer: buyers.py prints 205 (distinct users with a purchase); reproduced with awk since python is missing.

## Why the answer is unique
The script's definition is in its source.
