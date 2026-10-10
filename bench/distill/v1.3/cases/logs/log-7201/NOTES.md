## Traps
- TR-DECOY: the journal's first ERROR after the deploy banner belongs to tariff-engine (2026-08-22T09:13:05.927Z req=rq-9c41e7d2, "rate table v12 failed to load"), and a WARN from dispatch-api itself (2026-08-22T09:50:56.352Z req=rq-2b7f09a1, "pricing fell back to manual book") reads like a failure too. The first ERROR logged by dispatch-api itself is 2026-08-22T16:51:15.394Z req=rq-5f3a90c7; the tariff-engine error is another service's line and the WARN is not an ERROR. A later dispatch-api ERROR (2026-08-22T17:00:32.797Z) confirms "first" matters.

## Reference solution
1. Read README.md: line grammar, the five services, and that a line belongs to the service named in it.
2. Open the head of logs/dispatch-2026-08-22.log: the release banner sits on line 1, so every record line is post-release.
3. Search ERROR lines and walk them in order; the tariff-engine error (2026-08-22T09:13:05.927Z, rq-9c41e7d2) and the audit-mirror/inventory-sync errors come first but carry other services' names.
4. The first ERROR whose service field is dispatch-api is 2026-08-22T16:51:15.394Z, req=rq-5f3a90c7.

## Why the answer is unique
The service field is the third token of every record line, so "logged by the dispatch API itself" selects exactly the lines whose service is dispatch-api; the banner is line 1, so every record line is post-release and the earliest dispatch-api ERROR line is well-defined. The tariff-engine error and the dispatch-api WARN are decoys by level and by service, not alternative readings: a WARN is not an ERROR, and the tariff-engine line names tariff-engine. Exactly one request ID answers the question: rq-5f3a90c7.
