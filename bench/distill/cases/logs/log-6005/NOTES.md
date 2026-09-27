## Traps
- TR-DEFN: README.md defines a passage as complete only when the vessel leaves the chamber, but two of the nine boats that entered (Heron, Kittiwake) have no VESSEL OUT line that day. Counting VESSEL IN lines gives 9.

## Reference solution
1. List the workspace: README.md and logs/lock3-journal.log.
2. Read README.md: a passage completes when the entering vessel leaves the chamber; vessels still in the chamber overnight finish the next morning.
3. Read logs/lock3-journal.log and count boats with both a VESSEL IN and a VESSEL OUT line: Kestrel, Merlin, Grebe, Godwit, Ibis, Jackdaw, Goosander = 7.

## Why the answer is unique
The README pins the definition of a completed passage to the VESSEL OUT line, and the two boats without one are explicitly the vessels moored overnight, whose passages finish the next day. So the entrant count 9 is not a defensible reading of "completed passages"; only the intersection of IN and OUT boats counts. The answer is 7.
