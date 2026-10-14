## Traps
- None. The sheet names the required settings in one list and the filled-in ones in another, so the count follows straight from the two of them.

## Reference solution
1. List the workspace: `README.md`, `config/brine-pump.json` and a note under `docs/`.
2. Read `config/brine-pump.json`. The required list carries `restart_gap_min`, `duty_ceiling_pct`, `prime_revolutions`, `sump_alarm_min`, `pan_level_mm` and `flush_gap_min`; the values block fills in the first three only. The settings left without a value are `sump_alarm_min`, `pan_level_mm` and `flush_gap_min`, which is 3.

## Why the answer is unique
The sheet defines what "still has no value" means: a name is filled in when the values block carries it, and three of the six required names are absent from that block. The values block holds no name that the required list leaves out, so nothing is being counted twice or left over, and the pan floor note covers washing and inspection rather than controller settings. The answer is 3.
