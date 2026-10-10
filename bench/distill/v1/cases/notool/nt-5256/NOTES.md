## Traps
- TR-NOTOOLNEED: the case declares the zero-call contract (`expect.tools` is empty). The routes/stop-days.txt holds several entries in one list, so a reply taken from a neighbouring row gives Tuesday.

## Reference solution
1. Read routes/stop-days.txt; the entry for `Bramblecote` gives Friday (one lookup, matching ref_calls 1).

## Why the answer is unique
The list gives one value per entry and the README states it is edited in place, so the file records exactly one value for the asked entry. It also gives Tuesday for Withermoor, which is a different stop, so no other entry carries the asked day. The answer is Friday.
