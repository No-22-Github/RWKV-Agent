## Traps
- TR-DATEFMT: the loading dock writes day-first slashes (26/09/2026 = 26 September, 03/10/2026 = 3 October), the convention the README documents. Sorting the raw strings scatters them: 03/10/2026 lands first (its leading 0 sorts before every 2026- row) and 26/09/2026 lands after all the ISO rows. The days must be compared as real days while still being printed as written.

## Reference solution
1. Read queue.py: the docstring says oldest first and days printed as written.
2. Read jobs/2026-09.csv: JB-4404 is written 26/09/2026.
3. Read README.md: the loading dock writes day-first slashes, both spellings mean the same day.
4. Fix the ordering to compare real days (both spellings) while printing each day exactly as written.

## Why the answer is unique
Ordered by real day and printed as written, the merged run (the scoring run adds jobs/2026-10.csv with 03/10/2026 in it) prints exactly 2026-09-02,JB-4401 / 2026-09-11,JB-4402 / 2026-09-19,JB-4403 / 26/09/2026,JB-4404 / 2026-09-28,JB-4405 / 2026-10-02,JB-4501 / 03/10/2026,JB-4502 / 2026-10-15,JB-4503 and QUEUED,8. The README fixes the day-first reading of the slash rows, so the string sort is a misreading of the shop's own convention rather than a second defensible order, and the docstring keeps the printed spelling unchanged.
