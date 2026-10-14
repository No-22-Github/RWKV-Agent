## Traps
- none: every row of the day log belongs on the notice list, the README fixes
  the line shape, and no status filtering is involved. Base L0 of the family.

## Reference solution
1. Read README.md: notices/ takes one file per day named YYYY-MM-DD.txt, every log row becomes `- <name> / <seat>` in row order.
2. Read daylogs/2026-09-27.txt.
3. Write notices/2026-09-27.txt with the four lines.

## Why the answer is unique
The README lists everyone who took part regardless of sign-off status, so no
filter applies and the four rows give exactly four lines in the given order.
