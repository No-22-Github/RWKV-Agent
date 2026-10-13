## Traps
- Answer: 2147.
- Data volume: 1 data files, 80 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The answer sits in the last part of the file; a read that stops at 64KB sees an earlier match or none.

## Reference solution
1. bash: `grep ' db=events ' backup/runs.log | tail -1` -> 2147
Final answer: The most recent events backup was 2147 MB.

## Why the answer is unique
The log is append-only in time order; the last matching line is the latest.
