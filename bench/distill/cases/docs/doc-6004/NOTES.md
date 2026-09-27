## Traps
- TR-ABSENT: the terms sheet has no pet row. The nearest per-stay charge is `Linen hire per stay` at 25 GBP, and a solver that takes the other per-stay amount as the pet charge reports 25 instead of UNKNOWN.

## Reference solution
1. Read README.md: the sheet is the standing terms, and terms it does not list are settled with the house manager.
2. Read terms/booking-terms.csv: the rows are deposit, balance, cancellation, linen hire and late checkout; no pet term exists.
3. Read docs/arrival-notes.md: dogs are welcome at paw-flag cottages with no charge mentioned. The answer is UNKNOWN.

## Why the answer is unique
The README states that the sheet is the firm's standing terms and that anything beyond them is settled with the house manager for the cottage, so a term with no row has no figure to quote. The decoy 25 is the linen hire charge, the other per-stay amount on the sheet; reading one per-stay term as the other is the mistake the case is built around. The answer is UNKNOWN.
