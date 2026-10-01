## Traps
- TR-DECOY: sessions/archive/2026-08.csv holds the frozen pre-migration schedule with open-state rows; sweeping it recursively prints August sessions (decoy: sessions/archive rows printed with the flag)
- The scoring run also adds sessions/2026-10.csv the model never saw (expect.run.hidden_files), so a script that hardcodes the visible month fails the run check too.

## Reference solution
1. Read session_board.py and its docstring: live exports are sessions/*.csv at the top level; the board sorts by session date then session id.
2. Read README.md to confirm sessions/archive/ never prints.
3. Read sessions/2026-09.csv to see the state column values.
4. Add --open: filter rows whose state is open after the existing sort, leaving the no-flag behaviour untouched.

## Why the answer is unique
With the flag the board is the open rows of the live exports only, in the board's existing order: SN-4141,2026-09-03,Main Rink,open,6400 through SN-4149,2026-10-13,Studio Rink,open,8300 - five lines, no archive rows. The docstring and README both state that sessions/archive/ never prints, so there is no reading in which the August open rows belong on the board; and the scoring run's October export contributes two of the five lines, so a run against the September file alone also differs.
