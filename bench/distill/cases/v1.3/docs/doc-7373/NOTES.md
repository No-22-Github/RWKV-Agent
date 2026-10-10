## Traps
- TR-DUPROW: the reset log writes the Cave 7a teal set twice (the tablet
  re-keyed it); printing two cards for one set is the trap.
- TR-DECOY: the Traverse row is taped only - hold maintenance, not a route
  set - and gets no card.

## Reference solution
1. Read README.md: the card list takes one line `- <wall> <grade> <color>` per distinct set row in log order; re-keyed rows are one set and taped-only rows get nothing.
2. Read log/resets.txt.
3. Write cards/2026-09-25.txt with the Slab, Cave and Arete lines.

## Why the answer is unique
The repeated Cave row is the same wall, grade and color written twice, and the
README says each distinct set gets one card, so the second write cannot be a
second route. The Traverse row's status is taped only, which the README
excludes from carding. What remains is three distinct set rows whose fields
are copied verbatim, so the card list has exactly one content.
