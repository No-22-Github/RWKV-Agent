## Traps
- TR-SUPERSEDE: logs/purge-superseded.log holds the aborted attempt (9 QUEUED rows, aborted at 22:05 before anything was sent); the operator re-issued the same ids plus five new ones as the executed run. Adding both files' rows gives the decoy 23; only SENT rows were carried out, so the answer is 14.

## Reference solution
1. Turn 1: read README.md (the superseded attempt was aborted before sending; ids are stable; only SENT rows count), read both logs, count distinct ids with a SENT row: P-301..P-314 = 14. Answer: 14 purge.
2. Turn 2: of those, paths under /assets/covers/: P-301, 303, 305, 309, 312 = 5. Answer: 5 purge.
3. Turn 3: drop the marketing paths (P-306, P-310, P-314): 14 - 3 = 11. Answer: 11 purge.
4. Turn 4: minute with the most SENT rows in the executed run: 22:41 has 3 (P-310, P-311, P-312); every other minute has 1. Answer: 22:41.

## Why the answer is unique
The README pins the relationship between the two files (aborted attempt, re-issued unchanged ids, only SENT rows carried out), so summing both files is disqualified by the fixture itself; the executed run's rows are the sole record of what was carried out. Path prefixes partition the purges exactly (covers 5, marketing 3, others 6), and the minute histogram over the executed run's timestamps has a single maximum at 22:41.
