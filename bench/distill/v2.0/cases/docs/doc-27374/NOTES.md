## Traps
- none: four set rows, no re-keyed writes and no taped-only rows. Base L0 of
  the family.

## Reference solution
1. Read README.md: cards/ takes one file per reset day named YYYY-MM-DD.txt with `- <wall> <grade> <color>` per set row in log order.
2. Read log/resets.txt.
3. Write cards/2026-09-28.txt with the four lines.

## Why the answer is unique
Every row is a set, fields are copied verbatim, and line shape and order are
fixed by the README, so the card list has exactly one content.
