## Traps
- None declared. The scoring run adds a second monthly feed file the model never saw (expect.run.hidden_files, kept inside feeds/), and that file carries another aborted row, so a fix that only deletes the one bad September row fails on the next month.

## Reference solution
1. Read logs/night-2026-09-29.log: the crash is ValueError on int('') at the grams line.
2. Read feeds.py: its docstring already states aborted entries count nothing.
3. Read feeds/2026-09.csv: the 09-14 Ray Pool row has an empty grams cell, and fix feeds.py accordingly.

## Why the answer is unique
With aborted rows counted as nothing, the merged run (the scoring run adds feeds/2026-10.csv, whose 10-15 Reef Loop row is aborted the same way) prints exactly Kelp Shelf,1320 / Ray Pool,1080 / Reef Loop,3340 and TOTAL,5740. The docstring inside feeds.py pins the rule, so deleting the single September row is the only reading that contradicts it - the tablet's own aborted entry cannot be a feeding of zero grams because the docstring says such rows count nothing and the report is per tank.
