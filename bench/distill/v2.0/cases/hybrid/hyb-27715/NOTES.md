## Traps
- TR-DUPROW: jobs/print-jobs-2026-09.csv repeats PJ-9031 and PJ-9034 as identical extra rows.
  Summing rush rows gives 5260.00; deduplicating gives 3864.00.

## Reference solution
1. read_file README.md: the export retried, so a rush job can appear as two identical rows.
2. read_file jobs/print-jobs-2026-09.csv. Turn 1: distinct rush jobs total 3864.00 元. Turn 2: PJ-9031 at 980.00 is the largest rush job. Turn 3: its total is 980.00 元.

## Why the answer is unique
The two repeated rows are identical in all three columns and the README attributes them to an export retry, so the row sum 5260.00 double-counts two jobs that were each already present. Among the six distinct rush jobs, 980.00 is strictly the largest, so 3864.00, PJ-9031 and 980.00 are the only readings.

## Five alternative phrasings of the task
1. shiguang copy shop september rush jobs
2. rush job charges for september
3. which rush job cost the most
4. the top rush job's amount
5. september print jobs by rush flag
