## Traps
- TR-ABSENT: no source in the settings sheet defines `reservation_hold_s`. The neighbouring key `session_hold_s` is 1800 in the shipped defaults, and a solver that reads the two names as the same setting reports 1800 instead of UNKNOWN. The other four keys in the sheet resolve normally, so nothing about the question looks missing.

## Reference solution
1. List the workspace: `README.md`, `config/checkout-settings.json` and one note under `docs/`.
2. Read the settings sheet and walk the three blocks in `resolved_from`. `reservation_hold_s` is in none of them: the runner exports and profile blocks do not mention it, and the shipped defaults carry `session_hold_s`, which is a different setting. With no source defining it, the effective value cannot be determined, so the answer is UNKNOWN.

## Why the answer is unique
The README states that a setting takes its value from a source that defines it, and the sheet is the complete set of sources the service consults, so a key that no block mentions has no value at all. The decoy 1800 is the shipped default of `session_hold_s`, a different key whose name is close but whose value says nothing about the reservation hold; reading one key as the other is the mistake the case is built around. The answer is UNKNOWN.
