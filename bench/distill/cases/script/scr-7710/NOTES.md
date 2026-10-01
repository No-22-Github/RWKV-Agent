## Traps
- TR-DECOY: logs/night-2026-09-26.log opens with a warning about the battery archive moving to archive/2026-08; chasing that routine housekeeping leaves the ValueError in place.

## Reference solution
1. Read logs/night-2026-09-26.log: the crash is ValueError on int('') at the bikes line.
2. Read swaps.py: it feeds every bikes cell straight into int().
3. Read swaps/2026-09.csv: SW-5105's bikes cell is empty.
4. Read README.md and fix swaps.py so a row with an empty bikes cell counts nothing, per the docstring.

## Why the answer is unique
With unfinished swaps counted as nothing, the merged run (the scoring run adds swaps/2026-10.csv, whose SW-5203 is unfinished the same way) prints exactly Harbour Wall,20 / Mill Race,9 / North Lock,13 and TOTAL,42. The docstring inside swaps.py pins the rule for empty cells, so neither dropping the whole file nor skipping all of Mill Race can reproduce the report; the archive warning describes a move that the glob over swaps/*.csv never depended on.
