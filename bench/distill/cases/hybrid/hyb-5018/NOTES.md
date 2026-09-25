## Traps
None. One room card with one row per room, and the question names both the room and the
season the card prices separately.

## Reference solution
1. list_files: the workspace holds tariff/room-rates-2026.csv and README.md.
2. read_file tariff/room-rates-2026.csv: the double room row is 79 on the low season
   card and 96 on the high season card. The booking is a low season one, so the rate
   is 79.

## Why the answer is unique
The card gives one figure per room and season, and the question fixes both: the room is
the double and the season is the low one. 96 is the same room priced on the other card,
and 58, 71 and 104 belong to the single, twin and family rooms, so none of them can be
the nightly rate of a double room in the low season. The README confirms every room is
offered on both cards.

## Five alternative phrasings of the task
1. millgarth guest house room rates 2026
2. millgarth low season double room rate
3. guest house nightly rate card millgarth
4. millgarth room prices per night
5. millgarth tariff low and high season
