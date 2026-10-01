## Traps
- TR-DUPROW: in data/runs_export.csv three September Docklands runs (KR-2609100, KR-2609105, KR-2609109) were written twice by the retried export, and one September Midtown run plus one August Harbour Point run repeat as well (outside this task's filter). Counting rows gives 16; the README states run_id identifies the run and a retry rewrites the same run verbatim, so the answer is 13 distinct runs.

## Reference solution
1. Read README.md: run_id identifies a run; the export job retried and rewrote a few rows.
2. Aggregate: {{"path":"data/runs_export.csv","filter":{{"zone":"Docklands","run_month":"2026-09"}},"operation":"distinct_count","field":"run_id"}} gives 13.
3. Reply with the number 13 only.

## Why the answer is unique
The decoy 16 treats the repeated rows as different runs, but each repeat matches its original in every column and the README states run_id identifies the run, so there is no reading in which they are separate runs. August rows and September rows outside the Docklands zone fail the filter. The answer is 13.
