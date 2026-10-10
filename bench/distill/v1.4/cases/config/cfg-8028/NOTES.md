## Traps
- TR-ABSENT: neither config/tunnel-2.toml nor config/env/production.toml sets extract_ramp_s. docs/tunnel-config.md says the unset value falls back to the ramp built into the Hydromax PLC, which changed between firmware releases.
- TR-DECOY: config/tunnel-2.toml has rinse_hold_s = 40. The docs state it is the rinse chamber hold during drain cycles and is unrelated to extraction; reporting a 40-second ramp is the decoy answer.

## Reference solution
1. Read config/tunnel-2.toml: no extract_ramp_s; only rinse_hold_s = 40 and press.dwell_s.
2. Read config/env/production.toml: overrides load_belt_speed_m_min only.
3. Read docs/tunnel-config.md: unset ramp means the Hydromax PLC built-in, which varies by firmware release.
Final answer (2-4 sentences): extract_ramp_s is not set in either the base config or the production override, so production runs on the ramp built into the Hydromax PLC, and the repo does not record what that is for the firmware you ship. The rinse_hold_s = 40 in the file is the rinse chamber hold, not the extraction ramp. Confirm the PLC firmware version or pin extract_ramp_s in config/env/production.toml as the docs recommend. Criteria: mentions extract_ramp_s and Hydromax plus a not-set phrase; must not present 40 as the ramp.

## Why the answer is unique
The only extraction-adjacent number in the config belongs to rinse_hold_s, which the docs explicitly separate from extraction. The ramp key appears in neither file, so the effective value is the PLC built-in, which the workspace does not contain; answering with any number would be invented.
