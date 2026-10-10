## Traps
- TR-HEADER: the sheet ends with a HARBOUR TOTAL line whose nights value (117) clears the
  five-night test. A reader who counts every row over five nights includes it and reports 9
  vessels instead of 8.

## Reference solution
1. List the workspace: the August berth log and a readme.
2. Read README.md: the closing line is a month total, not a vessel.
3. Read berth_log_2026-08.csv and count stays with nights above five, leaving the total line
   out: 8.

## Why the answer is unique
The readme fixes the closing line as a harbour total and not a vessel: it has no arrival, no
departure and no berth, so it cannot be a stay. Every other row is one vessel stay, so the count
of stays beyond five nights is 8; including the total line is the decoy 9.
