## Traps
- TR-DUPROW: sowings/2026-09.csv carries MB-103 twice (tablet re-upload, rows identical). Counting it twice inflates the season line from 92 to 107 trays.
- TR-DATEFMT: MB-104 and MB-106 log their sowing days day-first with slashes (10/09/2026 = 10 September, 24/09/2026 = 24 September), the convention the README documents. Rows a reader cannot place get dropped: skipping the three slash-dated rows (the hidden October file carries 05/10/2026) puts the season line at 68 instead of 92, and leaving the days as raw strings breaks the oldest-first order.

## Reference solution
1. Read pottings.py: its docstring fixes the layout, the batch rule and the two day spellings.
2. Read sowings/2026-09.csv: MB-103 appears twice and two rows carry slash days.
3. Read README.md: the paper app writes day-first slashes; the report counts each batch once.
4. Write pottings.py: keep one row per batch_id, normalize slash days day-first, aggregate trays per day, print oldest first in the tablet's spelling, then the SEASON line.

## Why the answer is unique
With MB-103 counted once and both slash rows read day-first, the merged uploads (the scoring run adds sowings/2026-10.csv, which repeats MB-107 and carries 05/10/2026) print exactly 2026-09-03,20 / 2026-09-10,21 / 2026-09-18,9 / 2026-09-24,11 / 2026-10-02,10 / 2026-10-05,7 / 2026-10-15,14 and SEASON,92. The docstring and README together pin the batch rule and the day-first convention, so neither the re-uploaded row nor a month-first reading of the slash rows is a defensible second answer: the tablet's own uploads call the second copy a re-upload, and the README fixes which side of the slash the month sits on.
