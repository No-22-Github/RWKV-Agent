## Traps
- TR-DATEFMT: after the rotate the stamps are dd/mm/yyyy, so 1 February appears as 01/02/2026. Read day and month the ISO way round (month first) and 01/02/2026 becomes 2 January, whose ISO section shows an over-current ERROR from metherall-coiler-1. README.md documents the switch.

## Reference solution
1. List the workspace: README.md and logs/pickling-line.log.
2. Read README.md: stamps are ISO through January and dd/mm/yyyy from the February rotate on.
3. Read logs/pickling-line.log and take the unit from the ERROR line stamped 01/02/2026 = metherall-coiler-2 at 12:09.

## Why the answer is unique
The README fixes which sections of the file use which stamp order, so 01/02/2026 can only be 1 February; under that reading exactly one over-current ERROR falls on the asked-for day and it names one unit. The January-2 ERROR belongs to a different day and a different stamp style, and reaching it requires swapping the day and month fields the README spells out, which is the decoy. The answer is metherall-coiler-2.
