## Traps
- None declared. The scoring run adds mobs/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes what it read during exploration fails the run check.

## Reference solution
1. Read logs/flywatch-2026-09.log: NameError on flag in the print line.
2. Read fly_watch.py: the loop variable is row and the flag lives in the row dict.
3. Fix the print to use row['flag'].

## Why the answer is unique
The sheet prints each export row as its own line in export order; the only defect is the undefined flag in the print, and the fix - row['flag'] - leaves no second reading of the output, which is exactly 2026-09-15T17:44,Mob 9,watch through 2026-10-13T18:05,Mob 15,clear including the scoring run's October rows.
