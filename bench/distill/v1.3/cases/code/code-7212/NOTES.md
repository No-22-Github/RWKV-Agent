## Traps
- TR-CLAIM: the module header claims seal_valve is called from 11 places; the README counts real call expressions and says audit notes cannot be trusted, and the actual count is 13.
- TR-DECOY: the name seal_valve is echoed in a TODO comment (line 521) and a log template (line 925); counting text occurrences overshoots.

## Reference solution
1. Read README.md: the scope is ironhull/ and a call site is a real call expression.
2. Search the name seal_valve and read the line windows around the hits.
3. Keep only call expressions; drop the definition, the echoes and shut_valve_door.
4. The count is 13.

## Why the answer is unique
The README overrides quoted counts and defines call sites as call expressions; comments and log templates are not calls and shut_valve_door is a different function. The package holds exactly 13 call expressions of seal_valve.
