## Traps
- TR-ABSENT: no row in `periods.csv` covers a cattery booking. The first row, `Cancelling a kennel booking`, gives 14 days, and a solver that reads the kennel rows as covering the cattery reports 14 instead of UNKNOWN. The other rows resolve normally, so nothing on the page looks unanswerable.

## Reference solution
1. List the workspace: `README.md`, `periods.csv` and a page of booking notes.
2. Read `periods.csv`: the rows cover cancelling and moving a kennel booking and adding a day during a stay. Read the README: the cattery takes its own bookings and its terms sheet is held at the cattery rather than in this schedule. No row gives a notice period for a cattery place, so the answer is UNKNOWN.

## Why the answer is unique
The README states that the schedule is the kennels' schedule for kennel bookings and that the cattery's terms sheet is held elsewhere, so a cattery cancellation has no notice period in the set of documents at hand. The decoy 14 is the notice for cancelling a kennel booking, a different service whose schedule does not extend to the cattery; reading one as the other is the mistake the case is built around. The answer is UNKNOWN.
