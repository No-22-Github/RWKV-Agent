## Traps
- None declared. The scoring run adds casks/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes what it read during exploration fails the run check.

## Reference solution
1. Read pit_totals.py: it imports pandas only to concatenate, group and sum.
2. Read casks/2026-09.csv to confirm the columns.
3. Rewrite pit_totals.py with csv + glob: per pit a count and a minutes sum in name order, then TOTAL.

## Why the answer is unique
The per-pit sheet is fully pinned by the data: Cinder One has four firings for 136 minutes, Cinder Two three for 83, and the scoring run's October export lifts it to TOTAL,10,315. The rewrite must print the same bytes as the pandas version, whose groupby sorts pit names, so no other order or rounding is available.
