## Traps
- TR-DATEFMT: after the rotate the stamps are dd/mm/yyyy, so 1 April appears as 01/04/2026. Reading day and month the ISO way round makes that 4 January, a day the journal does not cover, so the misreading counts only the three 31 March starts and answers 3. README.md documents the switch.

## Reference solution
1. List the workspace: README.md and logs/press-journal.log.
2. Read README.md: stamps are ISO through March and dd/mm/yyyy from April on.
3. Read logs/press-journal.log and count run_start lines on 2026-03-31 (10:12, 14:05, 19:48) plus run_start lines stamped 01/04/2026 (06:10, 08:35, 11:02, 15:40) = 3 + 4 = 7.

## Why the answer is unique
The README fixes which stamp order each section uses, so 01/04/2026 can only be 1 April and the window covers exactly the 31 March ISO starts plus the 1 April dd/mm starts. Under that reading there are seven run_start lines and no second interpretation of either section. Dropping the April starts, the decoy 3, requires misreading the day and month fields the README spells out. The answer is 7.
