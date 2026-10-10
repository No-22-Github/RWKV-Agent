## Traps
- None. The sheet carries the required list and the configured values side by side, and the question asks for a plain count over those two blocks.

## Reference solution
1. List the workspace: `README.md`, `config/pressline.json` and a handover note under `docs/`.
2. Read `config/pressline.json`. Six parameters are required (`ram_force_kn`, `cycle_budget_ms`, `guard_delay_ms`, `die_temp_c`, `scrap_tolerance_pct`, `downtime_alarm_s`) and four of them have a value, so `scrap_tolerance_pct` and `downtime_alarm_s` are still unset: 2.

## Why the answer is unique
The README states what the two blocks mean, and the only reading the fixture supports is a comparison between them; nothing else in the workspace lists parameters. Counting the configured entries (4) or the required entries (6) answers a different question than the one asked, so the answer is 2.
