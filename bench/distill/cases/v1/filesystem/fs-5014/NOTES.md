## Traps
- None. One card exists per drying run and the amber malt run has its own card, so the drum is a single lookup rather than a choice between candidates.

## Reference solution
1. list_files (1): README.md and the three cards under batches/.
2. read_file batches/118-amber.txt (2): the card is the only amber malt run and its first line reads "Drum 4 - amber malt, 2.4 tonnes - loaded 06:40", so the drum is 4.

## Why the answer is unique
The three cards name three different malts, amber, brown and pilsner, and only one card is written for the amber malt batch, so no other card can answer the question. That card names a single drum on its load line, drum 4; the 2.4 tonnes on the same line is the load, not a drum. The answer is 4.
