## Traps
- TR-ABSENT: neither config/dryers.toml nor config/env/production.toml sets cool_down_hold_min. docs/dryer-config.md says the unset value is the controller's built-in cool-down hold, which changed between controller firmware versions.
- TR-DECOY: config/dryers.toml has anti_wrinkle_min = 20. The docs state it is the heatless post-load tumble and is not part of the temperature programme; reporting a 20-minute cool-down hold is the decoy answer.

## Reference solution
1. Read config/dryers.toml: no cool_down_hold_min; only reversing_s and anti_wrinkle_min = 20.
2. Read config/env/production.toml: overrides reversing_s only.
3. Read docs/dryer-config.md: unset hold means the controller built-in, which varies by firmware version.
Final answer (2-4 sentences): cool_down_hold_min is not set in either the base config or the production override, so production runs on the controller's built-in cool-down hold, and the repo does not record what that is for the firmware in service. The anti_wrinkle_min = 20 in the file is the heatless tumble after the load finishes, not the locked-door cool-down. Confirm the controller firmware version or pin cool_down_hold_min in config/env/production.toml; the docs also allow reading it off the controller at the machine. Criteria: mentions cool_down_hold_min plus a not-set phrase; must not present 20 as the hold.

## Why the answer is unique
anti_wrinkle_min is documented as the post-load heatless tumble, not the door hold while the load cools. The hold key appears in neither config, so the effective value is the controller built-in, which the workspace does not contain; any number would be invented.
