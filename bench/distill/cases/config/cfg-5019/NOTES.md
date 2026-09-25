## Traps
- TR-ABSENT: no block in the settings sheet defines `residual_hold_s`. The neighbouring key `contact_hold_s` is 420 in the factory defaults, and a solver that reads the two names as the same setting reports 420 instead of UNKNOWN. The other keys in the sheet resolve normally, so nothing about the question looks unanswerable.

## Reference solution
1. List the workspace: `README.md`, `config/dosing-settings.json` and a note under `docs/`.
2. Read the settings sheet and walk the three blocks in `resolve_order`. `residual_hold_s` is in none of them: the historian push and the site profile do not mention it, and the factory defaults carry `contact_hold_s`, which is a different setting. With no block defining it, the effective value cannot be determined, so the answer is UNKNOWN.

## Why the answer is unique
The README states that a setting takes its value from a block that defines it, and the sheet is the complete set of blocks the controller consults, so a key that no block mentions has no value at all. The decoy 420 is the factory default of `contact_hold_s`, a different key whose name is close but whose value says nothing about the residual hold; reading one key as the other is the mistake the case is built around. The answer is UNKNOWN.
