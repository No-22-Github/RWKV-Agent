## Traps
- TR-DECOY: logs/fridge-sep.log has a second above-range dip on 2026-09-06 tagged DEFROST (02:00 to 02:35). Ending the write-up at 02:35 folds the fridge's scheduled defrost cycle into the unplanned excursion; notes/maintenance.md says the defrost dips above range by design, so the excursion is 13:20 to 15:05 on 2026-09-04.

## Reference solution
1. Read notes/maintenance.md: cause is the door-seal gap; DEFROST dips are the scheduled monthly cycle, not excursions.
2. Read logs/fridge-sep.log.
3. The only EXCURSION opens at 13:20 on 2026-09-04 and the matching non-DEFROST recovery lands at 15:05.

## Why the answer is unique
The decoy 02:35 closes the scheduled defrost, not the excursion. The maintenance note states DEFROST cycles dip above range by design, so the 2026-09-06 pair cannot be unplanned; the only EXCURSION line is 13:20 and the only non-DEFROST recovery is 15:05. The cause line names the door-seal gap. Every required fact is anchored to the EXCURSION marker and the Cause: line, so no second reading exists.
