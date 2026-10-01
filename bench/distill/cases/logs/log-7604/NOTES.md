## Traps
- TR-HEADER: exports/circulation-june.csv ends with a GRAND TOTAL line reading "8 transactions". It counts every event line (checkouts, renewals, returns), so quoting it answers the checkout question with 8 instead of 5.

## Reference solution
1. Read README.md: each line is one event and the GRAND TOTAL counts every line whatever its kind.
2. Read exports/circulation-june.csv.
3. Count by event: 5 checkouts, 2 returns, 1 renewal.

## Why the answer is unique
The decoy 8 transactions is the file's own GRAND TOTAL line. README states that line counts every event line whatever its kind, and the file holds 5 checkout, 2 return and 1 renewal lines, so "8" answers a question nobody asked; the checkout count can only be 5. The event column has exactly three values and their tallies are 5/2/1, which fixes the breakdown too. A summary built on the event column lands on those three facts and no second reading exists.
