## Traps
- none: a single reading with its date and operator on the sheet. Base L0 of
  the family.

## Reference solution
1. Read README.md: a reading is logged as `<date> pump B runtime <h> h - pressure <bar> bar - operator <name>` under the sheet's date with the signing operator.
2. Read notes/meter-2026-09-27.txt.
3. Append the 2026-09-27 reading line to logs/runtime.log.

## Why the answer is unique
The sheet carries the date, the reading and the signing operator, and the line
shape is fixed by the existing log rows, so the appended line has exactly one
possible content.
