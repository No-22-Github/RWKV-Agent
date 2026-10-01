## Traps
- TR-DECOY: logs/irrigation-jul.log has two FAULT entries on 2026-07-21 tagged MANUAL TEST. Treating them as outage time stretches the incident to 10:02; notes/maintenance.md says those cycles ran in bypass with the valve already isolated, so the outage runs 04:10 to 05:00 on 2026-07-19.

## Reference solution
1. Read notes/maintenance.md: cause is the stuck V-3 solenoid; MANUAL TEST entries are bypass bench cycles, not outage time.
2. Read logs/irrigation-jul.log.
3. Real trouble opens with the first untagged FAULT at 04:10 on 2026-07-19 and ends with the tech's manual shutoff at 05:00.

## Why the answer is unique
The decoy 10:02 ends the window at the solenoid swap. The maintenance note states the 2026-07-21 MANUAL TEST faults ran in bypass with the valve already isolated, so they cannot extend the outage; the only untagged outage lines sit on 2026-07-19 between the first FAULT at 04:10 and the manual shutoff at 05:00. The cause line names the stuck V-3 solenoid. The window, its endpoints and the cause are each pinned by exactly one rule in the fixture, so the three facts have no second reading.
