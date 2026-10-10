## Traps
- TR-NOTOOLNEED: the case declares the zero-call contract (`expect.tools` is empty). The records/reading-units.txt holds several entries in one list, so a reply taken from a neighbouring row gives litres.

## Reference solution
1. Read records/reading-units.txt; the entry for `silage clamp weight` gives kilograms (one lookup, matching ref_calls 1).

## Why the answer is unique
The list gives one value per entry and the README states it is edited in place, so the file records exactly one value for the asked entry. It also gives litres for milk intake, which is a different reading, so no other entry carries the asked unit. The answer is kilograms.
