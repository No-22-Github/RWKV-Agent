## Traps
- TR-DECOY: retired/intake.py carries the same two calls and an intake path, so counting every module that calls record_weighing gives 5 instead of 3 for the intake and pond modules the question names.

## Reference solution
1. Read intake/loader.py: two calls to record_weighing, in load() and reload() (call 1).
2. Read pond/relay.py: one call inside relay() (call 2).
3. Read pond/store.py: the definition, which calls nothing, and retired/ holds a retired copy of the intake helpers that is outside the modules the question asks about (call 3). The three calls in intake/ and pond/ make the answer 3.

## Why the answer is unique
The decoy count 5 comes from the retired copy of the intake helpers: that module sits under retired/ and says in its own note that it was retired with the old grader, so it is not one of the modules the question asks about, and a call that no live module makes is not a call of the hatchery's intake. Every call in the intake and pond modules belongs to a module that imports the name from pond/store.py, and there are three of them, so the answer is 3.
