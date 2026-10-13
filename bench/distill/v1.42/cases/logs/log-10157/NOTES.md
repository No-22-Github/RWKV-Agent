## Traps
- Answer: 2026-08-19T0058.
- Data volume: 1 data files, 77 KB in all, so read_file (64KB) and bash output (8KB) cannot carry the raw rows; a pipeline has to compute the answer.
- The answer sits in the last part of the file; a read that stops at 64KB sees an earlier match or none.

## Reference solution
1. bash: `grep ' db=ledger ' backup/runs.log | grep ' result=failed$' | tail -1` -> 2026-08-19T0058
Final answer: The last failed ledger backup was at 2026-08-19T0058.

## Why the answer is unique
The log is append-only in time order; the last matching line is the latest.
