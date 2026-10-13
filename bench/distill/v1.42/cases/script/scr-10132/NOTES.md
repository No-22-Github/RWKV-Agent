## Traps
- Answer: checkout.
- Data volume: 5 data files, 27 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The sandbox has no python3, so running tools/worst_service.py fails with `command not found` (exit 127); the job's logic has to be read and reproduced.

## Reference solution
1. bash: `cat data/errors/*.csv | awk -F, '$3=="ERROR" {print $2}' | sort | uniq -c | sort -rn | head -3` -> checkout
Final answer: worst_service.py would print checkout (most ERROR rows); python is not available, so I reproduced it with awk.

## Why the answer is unique
The script's filter is in its source; reproducing it gives one result.
