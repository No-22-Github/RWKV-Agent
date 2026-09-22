## Traps
- TR-DATEFMT: contract_events.csv mixes three date styles - `2026/03/02`,
  `07-03-2026` and `Mar 11, 2026`. The README fixes the day-first convention
  for the bare-number styles. Read the ambiguous bare-number dates as
  month-first instead and the window membership changes at both ends:
  `03/04/2026` (3 April, outside) enters the window as 4 March, while
  `07-03-2026` (7 March, inside), `09-03-2026` (9 March, inside) and
  `01/03/2026` (1 March, inside) leave it - as 3 July, 3 September and
  3 January respectively. `14-03-2026` has no month-first reading (there is no
  fourteenth month), so a month-first reader falls back to day-first on that
  row and keeps it. Three rows out, one row in: the count comes out at 6
  (registered decoy) instead of 8.

## Reference solution
1. read_file README.md - bare-number dates are day-first; named-month entries
   are month-day-year (1)
2. read_file contract_events.csv - thirteen events across three date styles (2)
3. Parse each event_date under the stated convention: 2026-03-02, 2026-03-07,
   2026-03-11, 2026-04-03, 2026-02-24, 2026-03-14, 2026-02-28, 2026-03-09,
   2026-03-15, 2026-03-16, 2026-02-22, 2026-03-05, 2026-03-01 (3)
4. Keep the dates in the inclusive range 2026-03-01..2026-03-15: OST-4401,
   OST-4407, OST-4412, OST-4429, OST-4441, OST-4448, OST-4463, OST-4469 = 8 (4)

The answer is 8.

## Why the answer is unique
Every row carries exactly one date and the three styles are unambiguous once
the README's convention is applied: year-first entries fix their own order,
named-month entries fix theirs, and a bare-number entry is day-first by the
stated rule. Two rows touch the boundary (`2026/03/15` inside, `2026/03/16`
outside) and one sits just outside through a month swap (`03/04/2026`), so the
count is 8 and no other reading of the same rows yields 8. The decoy 6 is the
value reached only by reading the bare-number dates month-first, which
contradicts the README.
