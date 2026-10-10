## Traps
- TR-PRECEDENCE: config/orchard-base.json carries `label_delay_ms` 400 and profiles/packing-line.ini re-tunes it to 350 for harvest. A solver that reads the base file and stops reports 400.

## Reference solution
1. Read README.md: keys set in the profile's [packing-line] section replace the base values.
2. Read config/orchard-base.json: `label_delay_ms` 400 is the base value.
3. Read profiles/packing-line.ini: the [packing-line] section sets `label_delay_ms` 350, which replaces the base. The effective value is 350.

## Why the answer is unique
The README gives the profile the final say for any key it sets, and `label_delay_ms` is one of the two keys it sets, so the only reading that follows the stated resolution is 350. The decoy 400 is the base value, which applies only outside the seasonal profile; reading it as the harvest value is the mistake the case is built around. The answer is 350.
