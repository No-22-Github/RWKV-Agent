## Traps
- TR-NOTOOLNEED: the case declares the zero-call contract (`expect.tools` is empty). The services/collection-days.txt holds several entries in one list, so a reply taken from a neighbouring row gives Wednesday.

## Reference solution
1. Read services/collection-days.txt; the entry for `clinical waste` gives Tuesday (one lookup, matching ref_calls 1).

## Why the answer is unique
The list gives one value per entry and the README states it is edited in place, so the file records exactly one value for the asked entry. It also gives Wednesday for kerbside glass, which is a different waste stream, so no other entry carries the asked day. The answer is Tuesday.
