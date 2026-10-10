## Traps
- TR-ABSENT: oncall/2026-Q4.md has no tile-cache row; services/catalogue.md says tile-cache moved to the Platform Infrastructure pager tool on 2026-09-01 and is not in the shared rota.
- TR-DECOY: the rota does have a tile-cache-legacy row, and its Oct 19 entry is Kwame Osei. tile-cache-legacy was decommissioned on 2026-08-15, so naming Kwame Osei (or Rosa Lindeman from the same row) is the decoy answer.

## Reference solution
1. Read oncall/2026-Q4.md: no tile-cache row, only tile-cache-legacy.
2. Read services/catalogue.md: tile-cache is owned by Platform Infrastructure and paged from their own tool since 2026-09-01; tile-cache-legacy is decommissioned.
3. Cross-check the Oct 19 column of the legacy row, confirming it cannot be used.
Final answer (2-4 sentences): the shared Q4 rota has no tile-cache row, so it cannot say who is on call for tile-cache the week of Oct 19; the tile-cache-legacy row belongs to a service decommissioned in August, so those engineers are not on call for the live service. Per the service catalogue, tile-cache is owned by Platform Infrastructure and has been paged from their own tool since Sep 1 — check with Platform Infrastructure or their pager schedule. Criteria: mentions tile-cache and Platform Infrastructure (or a not-in-the-rota phrase); must not name the legacy row's engineers.

## Why the answer is unique
The legacy row's engineers are the decoy on object and status: the catalogue marks tile-cache-legacy decommissioned with its rotation only kept until the rota is regenerated, so its pager no longer answers for the live service. streets-renderer, mosaic-scheduler and gazetteer-api are other services. The catalogue states tile-cache left the shared rota, and nothing else in the workspace lists a tile-cache rotation, so the only correct reply is that the rota does not cover it and Platform Infrastructure does.
