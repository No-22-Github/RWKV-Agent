## Traps
- None. The schedule carries one row for moving a booking and states its notice in days.

## Reference solution
1. List the workspace: `README.md`, `periods.csv` and a page of park notes.
2. Read `periods.csv`: the row `Moving a booking to another date,21` gives the notice for the change the customer is asking about, which is the answer.

## Why the answer is unique
The schedule keeps one row per change, and only the moving row matches the request: 21 days. The two cancellation rows set 10 days for a touring pitch and 35 for a seasonal pitch, which are periods for ending a booking rather than moving one, and the park notes give the season dates and where the warden lives without setting a notice at all. The answer is 21.
