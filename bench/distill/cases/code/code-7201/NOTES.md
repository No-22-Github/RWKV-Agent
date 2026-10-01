## Traps
- TR-DECOY: in the canonical source the name route_shard appears before the definition — a TODO comment (line 417, "route_shard should honor the drain window"), a real call site (line 865, inside ShardRouter.plan_for_stream), and a log template string (line 1057, "route_shard fallback engaged for tenant %s"); pools.py adds an import mention. Taking the first hit or the call site as the definition answers with the wrong line. The definition is the single `def route_shard(` line, 1951, deep enough that a whole-file read stops short of it.

## Reference solution
1. Read README.md: it names shardkeeper/routing.py as the canonical source whose line numbers the package quotes.
2. Search the name route_shard: four hits inside the canonical file (comment 417, call site 865, log template 1057, definition) plus an import in pools.py.
3. Read line windows around the comment and call-site hits to rule them out.
4. The `def route_shard(` line in shardkeeper/routing.py is line 1951.

## Why the answer is unique
The README pins the canonical source file, so line numbers come from exactly one file; pools.py mentions route_shard only as an import, and a definition is a `def` line. Inside the canonical file the name appears in a comment, a call site and a log template — all excluded by "defined" — leaving exactly one `def route_shard(` line at 1951. The answer is 1951.
