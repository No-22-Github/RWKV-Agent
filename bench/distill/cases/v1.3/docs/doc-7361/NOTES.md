## Traps
- TR-DECOY: daylogs/2026-09-24.txt carries five rows but Yusuf Demir is
  provisional (rides along, not signed off). Writing five roster lines is the
  trap; only the four cleared rows belong on the roster.

## Reference solution
1. Read README.md: rosters live in rosters/ named YYYY-MM-DD.txt and list only rows with status cleared, one line `- <name> (<seat>)` in row order.
2. Read daylogs/2026-09-24.txt.
3. Write rosters/2026-09-24.txt with the Sander, Petra, Nadia and Colm lines.

## Why the answer is unique
A row is on the roster exactly when its third field reads cleared; Yusuf Demir's
row reads provisional and the note says he rides along without sign-off, so
listing him would mean inventing a clearance the log does not carry. Row order
and the `- <name> (<seat>)` shape are fixed by the README, so the four cleared
rows give exactly one roster.
