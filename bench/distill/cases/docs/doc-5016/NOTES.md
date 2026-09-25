## Traps
- TR-ABSENT: the charges sheet lists a packing service, a piano move, wardrobe box hire, storage and an extra stop, and it has no row for taking a fitted wardrobe down and putting it back together. The neighbouring row `Wardrobe box hire each` is 21.50, and a solver that reads that row as covering the customer's request reports 21.50 instead of UNKNOWN.

## Reference solution
1. List the workspace: `README.md`, the charges sheet under `fees/` and an office note under `docs/`.
2. Read `fees/charges.csv`: the five listed services are priced, and fitted wardrobe work is not among them; the README states that work the sheet does not list is quoted by the office after a survey, so no charge for it exists in the folder. The answer is UNKNOWN.

## Why the answer is unique
The sheet is the firm's complete price list and the README states how unlisted work is priced, so a service with no row has no figure to report. The decoy 21.50 is the wardrobe box hire charge, which prices a box the customer packs rather than work on a fitted wardrobe, so reading one as the other is the mistake the case is built around. The answer is UNKNOWN.
