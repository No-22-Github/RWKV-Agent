## Traps
- none: a single dispensary row, no pharmacy routing and no filtering. Base
  L0 of the family.

## Reference solution
1. Read README.md: dispensary rows become `<date> <patient> - <item> - dispensed - <vet>` lines in the monthly ledger.
2. Read notes/scripts-2026-09-30.txt.
3. Append the Nutmeg line dated 2026-09-30.

## Why the answer is unique
The sheet carries one patient with its date, item and vet, and the line shape
is fixed by the existing ledger rows, so the appended line has exactly one
possible content.
