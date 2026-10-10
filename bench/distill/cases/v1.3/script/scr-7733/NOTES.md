## Traps
- TR-NEARNAME: logs/sack-2026-09.log names pickers/2026-09-picks.csv while the tablets write pickers/2026-09.csv (decoy: FileNotFoundError from the retired export name)
- The scoring run also adds pickers/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read logs/sack-2026-09.log: FileNotFoundError on pickers/2026-09-picks.csv.
2. Read sack_tally.py: the path is hardcoded to the retired export name.
3. List/read pickers/ to see the actual file named for its month (pickers/2026-09.csv).
4. Fix sack_tally.py to sweep pickers/*.csv so the tally keeps working for later months.

## Why the answer is unique
The traceback names pickers/2026-09-picks.csv, which no longer exists; the tablets write pickers/2026-09.csv (README: one export per month, named for its month). The fixed tally sweeps the folder, so the scoring run's October export joins the sheet and the beds print as Drift Bed,4,560 and Sable Bed,5,817, ending TOTAL,9,1377. Re-creating a file under the retired name is not available: the exports stay untouched.
