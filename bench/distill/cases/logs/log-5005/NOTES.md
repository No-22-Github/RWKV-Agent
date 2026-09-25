## Traps
- None. The journal lists every scan for the day and each delivered line quotes the parcel id of its out line, so the parcels without a delivered line are plain to read off.

## Reference solution
1. List the workspace: README.md and logs/scans.log.
2. Read logs/scans.log. Twelve parcels are scanned out (P-40218, P-40223, P-40237, P-40244, P-40251, P-40266, P-40273, P-40288, P-40295, P-40302, P-40319, P-40326) and nine of them come back with a delivered line, so P-40218, P-40295 and P-40326 are the three without one.

## Why the answer is unique
The question asks for parcels that left the depot and were never handed over, and README.md says a parcel that comes back unsold gets no delivered line, so the delivered lines are exhaustive: a parcel with no delivered line was not handed over. Twelve out lines and nine delivered lines leave exactly three parcels unaccounted for. Counting the out lines instead of the parcels (12) or counting every line (21) answers different questions, and the answer to this one is 3.

## Fixture notes
README.md states both event kinds and their meaning. Every parcel id carries the same prefix and appears at most twice, once per event kind, so no parcel is scanned out twice or handed over twice.
