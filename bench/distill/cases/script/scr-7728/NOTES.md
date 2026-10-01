## Traps
- TR-DUPROW: shearings/2026-09.csv repeats FW-3004 and FW-3005 and the hidden export repeats FW-3103; counting rows double-counts pickups (decoy: pickup row counts (the re-sent pickups double-counted))
- The scoring run also adds shearings/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read shedbook.py: the docstring fixes the layout and the per-pickup_id counting.
2. Read README.md: repeated rows are identical copies of the same pickup_id.
3. Read shearings/2026-09.csv to confirm the repeats (FW-3004, FW-3005).
4. Write shedbook.py: count each pickup_id once, aggregate per pickup_date, print in date order, then TOTAL.

## Why the answer is unique
The docstring and README both state one row per pickup_id: FW-3004 and FW-3005 are re-sent copies, so 2026-09-09 prints 2,81 and 2026-09-16 prints 1,41, and the sheet ends TOTAL,11,424. Counting rows instead gives 9 September pickups and a doubled kg total, and the hidden October export repeats FW-3103, so a row-counting script fails there too.
