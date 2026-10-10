## Traps
- TR-DECOY: logs/deck-oven-aug.log carries two TEST BURN entries on 2026-08-15 (commissioning runs with the rack empty). Counting every over-limit line gives 4 over-temp alarms; notes/maintenance.md says test burns are expected and are not faults, so the genuine count is 2.

## Reference solution
1. Read notes/maintenance.md: the cause lives on its Cause: line, and the note rules the TEST BURN entries out as faults.
2. Read logs/deck-oven-aug.log.
3. Keep the ALARM lines without TEST BURN: two alarms on 2026-08-14, the first at 05:02; cause reads "worn heating element in chamber B".

## Why the answer is unique
The decoy 4 over-temp alarms counts the two TEST BURN entries of 2026-08-15 as faults. The maintenance note rules them out explicitly (commissioning runs, rack empty, expected), and they sit on the day after the element was swapped under WO-2214, so no reading of the log makes them part of the fault story. Every remaining over-limit line is tagged ALARM on 2026-08-14, giving 2 alarms with onset 05:02 and the cause stated on the Cause: line, so the three required facts follow from that single reading.
