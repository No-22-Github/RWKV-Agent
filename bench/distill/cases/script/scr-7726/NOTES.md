## Traps
- TR-MISSING: casks/2026-09.csv row 2026-09-04 Cinder One carries an empty minutes cell; dropping the whole row drops its 1870 pence (decoy: the empty-minutes day's pence dropped from the sheet)
- The scoring run also adds casks/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read logs/nightly-2026-09.log: int(row["minutes"]) crashes on the empty cell.
2. Read casks.py: the docstring says an empty minutes cell counts zero minutes but still contributes its pence.
3. Read casks/2026-09.csv to confirm the empty cell and the pence column.
4. Fix casks.py to treat an empty minutes cell as 0 while still adding the row's pence.

## Why the answer is unique
The docstring fixes the rule: an empty minutes cell counts zero minutes but still contributes its pence, so 2026-09-04 prints 27,4015 and the sheet ends TOTAL,243,23435. A fix that drops the whole row loses that day's 1870 pence and lands on a different TOTAL, and the hidden October export carries an empty cell of its own, so a September-hardcoded script also differs.
