## Traps
- TR-DECOY: `ingest/relay.py` keeps a withdrawn call in a comment ("# post_reading(row) was withdrawn with the spring replay"). Counting every line that reads like a call gives 4 instead of 3.

## Reference solution
1. List the workspace: the service is `ingest/` (pump.py, relay.py) with the readings store and audit under `meters/` (call 1).
2. Read ingest/pump.py: one call, inside pump() (call 2).
3. Read ingest/relay.py: one call inside relay(); the line in replay() is a comment, so it calls nothing (call 3).
4. Read meters/audit.py: one call inside audit() (call 4). The three real call sites are in pump(), relay() and audit(), so the answer is 3; meters/store.py holds the definition and calls nothing.

## Why the answer is unique
The decoy count 4 comes from reading the commented-out line in ingest/relay.py as a call: a comment is not executed and neither binds nor passes a reading, and the module's own replay() only returns its argument. Every other mention of the name in the workspace is either the definition in meters/store.py or an import line. The answer is 3.
