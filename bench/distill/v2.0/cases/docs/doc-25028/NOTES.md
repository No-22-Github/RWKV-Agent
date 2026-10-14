## Traps
- None. The schedule carries one row for a shortfall on a delivery and states its deadline in days from the delivery.

## Reference solution
1. List the workspace: `README.md`, `claims.csv` and a page of wholesale notes.
2. Read `claims.csv`: the row `Shortfall on a delivery,6` gives the deadline for the claim the wholesaler is making, which is the answer.

## Why the answer is unique
The schedule lists one row per kind of claim, and a delivery that arrives short falls under the shortfall row: 6 days from the delivery. The other rows cover a vat whose quality is challenged and a pallet being returned, which are different events with their own deadlines, and the wholesale notes cover who collects orders and how vats are marked without giving a deadline. The answer is 6.
