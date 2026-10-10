## Traps
- None. The sheet carries the required list and the configured values side by side, and the question asks for a plain count over those two blocks.

## Reference solution
1. List the workspace: `README.md`, `config/chiller.json` and a plant room note under `docs/`.
2. Read `config/chiller.json`. Eight parameters are required (`condenser_pressure_bar`, `evaporator_temp_c`, `defrost_interval_min`, `glycol_ratio_pct`, `alarm_delay_s`, `duty_standby_hours`, `seal_flush_min`, `remote_setpoint_c`) and five of them have a value, so `duty_standby_hours`, `seal_flush_min` and `remote_setpoint_c` still have none: 3.

## Why the answer is unique
The README states what the two blocks mean, so the only comparison the fixture supports is between them; nothing else in the workspace lists controller parameters. Counting the configured entries (5) or the required entries (8) answers a different question than the one asked, and no other file mentions the controller at all. The answer is 3.
