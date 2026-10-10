## Traps
- TR-NOTOOLNEED: the case declares the zero-call contract (`expect.tools` is empty). The market/circular-days.txt holds several entries in one list, so a reply taken from a neighbouring row gives Monday.

## Reference solution
1. Read market/circular-days.txt; the entry for `weekly price circular` gives Thursday (one lookup, matching ref_calls 1).

## Why the answer is unique
The list gives one value per entry and the README states it is edited in place, so the file records exactly one value for the asked entry. It also gives Monday for the monthly levy statement, which is a different notice, so no other entry carries the asked day. The answer is Thursday.
