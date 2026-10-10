## Traps
- TR-SUPERSEDE: prior/availability.txt (effective 2026-06-14) still shows the
  pea at 35 packets and the poppy at 8; the 2026-09-19 sheet in effect says 18
  and 25. Working from the June sheet is the trap.
- TR-DECOY: the September sheet carries four rows, but kale and Welsh onion
  are both noted as on hold and must stay off the handout; listing all four is
  the second trap.

## Reference solution
1. Read README.md: the handout lists rows of the sheet in effect whose note does not put them on hold, one line `- <variety> (<packets> packets)` in sheet order.
2. Read both sheets and compare effective dates: 2026-09-19 beats 2026-06-14.
3. Read the rows of current/availability.txt and drop the two on-hold rows.
4. Write handouts/2026-09-29.txt with the pea and poppy lines.

## Why the answer is unique
The handout can only take rows that are both in stock (September sheet, not the
superseded June one) and not on hold (kale and Welsh onion are reserved by
note), and the README fixes line shape and order. Any other combination either
uses superseded quantities or hands out reserved seed, so exactly one handout
is possible.
