## Traps
- None. One sheet, one row per volume, and price is a plain two-decimal column.

## Reference solution
1. List the workspace: the June acquisitions sheet and a readme.
2. Read acquisitions_2026-06.csv and count Fiction rows priced under 8.00: 5.

## Why the answer is unique
Each volume has exactly one shelf and one price, so the only count the sheet supports is the
number of Fiction rows below 8.00, which is 5. No title of any shelf is priced between 7.90 and
8.10, so the boundary cannot be read the other way.
