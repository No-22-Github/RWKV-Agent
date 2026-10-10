## Traps
- TR-TZ: the journal stamps on plant time, two hours ahead of UTC, while the window is given in UTC. Reading the stamps as UTC and counting openings in the file's 20:00-21:00 finds 3; the UTC window maps to 22:00-23:00 plant time, where 5 gates open.

## Reference solution
1. List the workspace: README.md and logs/intake-journal.log.
2. Read README.md: the controller stamps on plant time, two hours ahead of UTC, so 20:00-21:00 UTC is 22:00-23:00 plant time.
3. Read logs/intake-journal.log and count GATE OPEN lines in 22:00-23:00: 22:04, 22:19, 22:33, 22:47, 22:58 = 5.

## Why the answer is unique
The README fixes the clock the stamps are on and the prompt fixes the clock the window is given in, so the window maps to one hour of the journal with no choice left. OPEN lines are the record of a gate opening; the CLOSE lines in the same hour are different events. The decoy 3 comes from taking the plant stamps as UTC. With the conversion applied the answer is 5.
