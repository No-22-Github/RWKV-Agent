## Traps
- None. The log holds one mains failure on 5 September 2026 and the run it started has a single STOP line carrying the duration, so the number is read off that line.

## Reference solution
1. List the workspace: README.md and logs/genset.log.
2. Read logs/genset.log. The 5 September events are MAINS lost at 04:12:07, START at 04:12:19, MAINS restored at 08:41:52 and the STOP line `2026-09-05T08:42:06Z STOP genset=G-1 run_seconds=16187`, so the generator ran 16187 seconds.

## Why the answer is unique
README.md says every generator run adds exactly one STOP line and that the STOP line carries the run's duration, so the duration is a recorded value rather than something to work out from the stamps. The only run that begins on 5 September ends with run_seconds=16187; the other STOP line in the file belongs to 28 September, and the three TEST lines are no-load runs. Reading the interval between the stamps instead (16187 seconds is 4h29m47s, which is the same span) or reporting the 28 September run answers a different question.

## Fixture notes
The three TEST lines carry the same run_seconds value, which is the controller's fixed no-load run rather than a measured one. All stamps are UTC and the closing line accounts for every event line.
