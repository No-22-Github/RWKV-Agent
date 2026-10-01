## Traps
- TR-SUPERSEDE: prior/availability.txt (effective 2026-05-30) still lists
  Scarlet runner bean at 40 packets and Borage at 11; the sheet in effect for
  2026-09-28 is the 2026-09-12 sheet, where the bean is down to 22 and Borage
  is gone. Copying the May sheet is the trap.

## Reference solution
1. Read README.md: the handout lists the varieties from the availability sheet in effect, one line `- <variety> (<packets> packets)` in sheet order.
2. Read both availability sheets and compare their effective dates: 2026-09-12 beats 2026-05-30.
3. Read the rows of current/availability.txt.
4. Write handouts/2026-09-28.txt with the bean, chamomile and rye lines.

## Why the answer is unique
The README pins the handout to the sheet in effect, and the effective dates in
the sheet headers decide which one that is for a 2026-09-28 handout: the
September sheet supersedes the May sheet, so 40 packets and Borage are archive
values, not stock values. Quantities and names come verbatim from one sheet,
so the handout has exactly one possible content.
