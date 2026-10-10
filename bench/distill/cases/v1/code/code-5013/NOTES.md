## Traps
- None. No trap tag is set: the verdict log carries one line per check, and the runner in checks/ writes exactly those lines.

## Reference solution
1. Read results/run-2026-09-14.log: five lines, each a check name and its outcome, and exactly two of them end in error (call 1).
2. Read checks/forgechecks.py to confirm the line shape the runner writes, which is <check> <outcome> (call 2). The count is 2.

## Why the answer is unique
The runner records one line per check and prints the outcome the run reached, so the log is the record of that run and nothing else: oven_draft and quench_temp came out as error, the other three as ok. There is no second reading of a five-line log with one outcome per line, and no figure in the log but the two error marks, so the count is 2.
