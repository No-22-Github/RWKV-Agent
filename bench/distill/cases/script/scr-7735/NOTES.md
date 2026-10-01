## Traps
- None declared. The scoring run adds trails/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes what it read during exploration fails the run check.

## Reference solution
1. Read trail_status.py: rows sort by checked date then trail.
2. Read trails/2026-09.csv to confirm the columns.
3. Add --day YYYY-MM-DD: after the existing sort, print only the rows for the requested date.

## Why the answer is unique
With the flag the sheet prints the requested date's rows in the sheet's existing order: 2026-10-04,Eagle Run,open and 2026-10-04,Heron Spur,cleared. Both rows come from the scoring run's October export, so a script that filters the September file alone prints nothing and differs; the no-flag behaviour is untouched by construction.
