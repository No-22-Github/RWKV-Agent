## Traps
- TR-NEARNAME: report.py opens downloads/reservations.csv while the feed writes dated names (reservations-2026-09.csv); the FileNotFoundError names the path that never exists.
- TR-DECOY: downloads/ still holds the mirror copy of August. Sweeping every file gives TOTAL 9 over two months instead of the newest month's 6 (and 5 once October lands).

## Reference solution
1. Read logs/feed-2026-09-30.log: the crash is FileNotFoundError on downloads/reservations.csv.
2. Read report.py: it opens one fixed name.
3. Read README.md: the feed writes one dated file per month and the report covers the newest month only.
4. Read downloads/reservations-2026-09.csv to confirm the columns.
5. Read downloads/reservations-2026-08.csv (the mirror copy) and fix report.py to pick the newest dated file by name.

## Why the answer is unique
Picking the newest dated file, the merged run (the scoring run adds reservations-2026-10.csv) prints exactly 2026-10-07,2 / 2026-10-14,1 / 2026-10-21,1 / 2026-10-28,1 and TOTAL,5. The docstring pins the newest-month rule and the README explains why August is still present, so folding August in is the mirror's own artifact rather than a reading of the report; a hardcoded September name fails the moment the October file lands, and there is no file in downloads/ that the traceback's path could name.
