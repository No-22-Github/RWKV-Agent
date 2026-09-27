## Traps
- TR-DUPROW: two Dunwich Academy lines (PR-6215 and PR-6218) were re-issued by the scheduling export
  and appear twice unchanged. Counting rows reports 9 runs; counting distinct run_ids gives 7.

## Reference solution
1. List the workspace: the August run log, a readme and an unrelated ink note.
2. Read README.md: re-confirmed runs are re-issued as identical lines.
3. Read press/runs_2026-08.csv and count the distinct run_ids for Dunwich Academy: 7.

## Why the answer is unique
The readme states that a re-issued line is the same run re-confirmed, and the repeated lines match
on every column, so they cannot be additional runs. Work is invoiced per run, which fixes the
count at 7; the row count 9 would bill two runs twice.
