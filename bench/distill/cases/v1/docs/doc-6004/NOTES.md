## Traps
- TR-ABSENT: the terms sheet has no pet row. The nearest per-stay charge is `Linen hire per stay` at 25 GBP, and a solver that takes the other per-stay amount as the pet charge reports 25 instead of UNKNOWN.

## Reference solution
1. Read README.md, terms/booking-terms.csv and docs/arrival-notes.md.
2. terms/booking-terms.csv carries deposit, balance, cancellation, linen hire and late checkout, and no pet term exists on the sheet; README.md states terms that are not on the sheet are settled directly with the house manager, and the arrival notes welcome dogs with no charge mentioned. No per-stay pet charge exists in the folder.
3. Final answer in two or three sentences: name the files checked, say the terms sheet has no pet term and so no per-stay pet charge, and point to the other per-stay item (linen hire) as a different term without quoting its amount. Scored with output_contains_any over "pet", "pet charge" or "charge for a pet"; output_excludes rules out UNKNOWN and the 25 linen-hire figure, so the reply names the missing term instead of quoting any amount.

## Why the answer is unique
README.md states that the sheet is the firm's standing terms and that anything beyond them is settled with the house manager for the cottage, so a term with no row has no figure to quote. The decoy 25 is the linen hire charge, the other per-stay amount on the sheet; reading one per-stay term as the other is the mistake the case is built around. The only truthful reply reports the absence: the terms sheet, README.md and the arrival notes were checked, no pet term exists on the sheet, and the other per-stay row is a different item whose amount is not the answer to the question.
