## Traps
- TR-DECOY: the old firmware raised six ERROR lines with code G-88 in the first hour, all of them recorded earlier in the file than the cutover marker and more numerous than anything on the new version. Taking the first ERROR in the file gives G-88.

## Reference solution
1. List the workspace: README.md and logs/gate-journal.log.
2. Read README.md: the cut over is announced in the journal and the gates run the new version from that line on.
3. Read logs/gate-journal.log: the cutover marker sits at 01:12:00; the first ERROR stamped later is at 01:38 with code G-91.

## Why the answer is unique
The cutover marker splits the file into two regimes and the question asks for the first ERROR in the second regime, so the G-88 errors recorded under the old firmware fail the condition regardless of how prominent they are. The new firmware's alarms carry one code, so once the marker is applied the first qualifying line is unambiguous. The answer is G-91.
