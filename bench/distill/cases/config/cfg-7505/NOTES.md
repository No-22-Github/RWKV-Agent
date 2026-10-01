## Traps
- TR-DECOY: envs/staging.env 的 REPLICA_REGION=cn-tianjin-1 与 prod 相邻易混，CACHE_TTL 两边相同也不是差异项。 A careless pass reports `cn-tianjin-1`.

## Reference solution
1. Read envs/prod.env and envs/staging.env.
2. Compare key by key; CACHE_TTL_SECONDS and LOG_LEVEL match, so they are not drift.
3. List the differing keys with the prod values verbatim, and cross-check the region against replica-map.list.

## Why the answer is unique
CACHE_TTL_SECONDS and LOG_LEVEL are identical on both sides, so the drift is exactly REPLICA_REGION, BACKFILL and MAINTENANCE_WINDOW. replica-map.list confirms prod writes from cn-beijing-2, so the staging values (cn-tianjin-1, on, SUN 03:00-05:00) never enter the prod column.
