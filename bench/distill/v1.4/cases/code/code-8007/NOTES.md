## Traps
- TR-ABSENT: no file defines pack_health_score; docs/scoring.md records it as removed on 2026-08-31, when scoring moved to the telemetry service.
- TR-NEARNAME: battery/health.py defines the similarly named pack_health_index (a 0-100 dashboard approximation). Presenting it as pack_health_score is the decoy answer.

## Reference solution
1. Search for pack_health_score: no definition; only the docs/scoring.md note about the removal.
2. Read docs/scoring.md and the battery package: the index is a different 0-100 dashboard metric.
Final answer (2-4 sentences): pack_health_score is not defined in this repo any more: the battery package only has the similarly named pack_health_index, a 0-100 dashboard approximation that is not the same metric. docs/scoring.md records the old score as removed on 2026-08-31, when scoring moved to the telemetry service. The warranty team should get the exact weights from the telemetry service. Criteria: mentions pack_health_score and a removed/telemetry phrase; must not present battery/health.py as the definition site.

## Why the answer is unique
pack_health_index has a different scale and purpose, and docs/scoring.md states it does not replace the removed score, so presenting it as pack_health_score is the decoy answer. No file in the workspace defines pack_health_score, so the only defensible reply is that the function is gone and where the metric lives now.
