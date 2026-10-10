## Traps
- TR-DUPROW: job_log_2026-07.csv reprints five job rows, so counting the data lines gives 70 jobs.
- TR-HEADER: the file ends with a `TOTAL` line, which adds one more line to any naive count and gives 71.

## Reference solution
1. List the workspace: the job log and a short readme.
2. Read README.md: one row per job, and the export was re-run.
3. Read job_log_2026-07.csv, step past the `TOTAL` line and count the distinct job_id values: 65.

## Why the answer is unique
The readme states one row per job, and each reprinted line repeats its job_id and every other field exactly, so
the repeats are the same job written twice. The `TOTAL` line carries no job_id and sums the sheets column, so it
is not a job either. Counting distinct job identifiers across the real rows gives 65.
