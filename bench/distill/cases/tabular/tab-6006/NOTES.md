## Traps
- TR-DATEFMT: completion dates mix ISO, slash and month-name styles, and the readme fixes the
  slash style as day first. The job dated 03/04/2026 was completed on 3 April and belongs in the
  week; a reader who swaps the fields files it under 4 March and totals 30.75 instead of 37.25.

## Reference solution
1. List the workspace: the job log and a readme.
2. Read README.md: slash dates are day-month-year.
3. Read jobs_april_2026.csv, resolve every completion date, keep 1-7 April 2026, and total the
   hours: 37.25.

## Why the answer is unique
The readme removes the day-month ambiguity for slash dates, so 03/04/2026 can only be 3 April,
inside the billed week, while 09/04/2026 and 18/04/2026 can only be April days outside it. The
month-name and ISO rows carry their own unambiguous months, and no row besides the 03/04 one
changes sides under a field swap that respects the readme. The week's hours are 37.25.
