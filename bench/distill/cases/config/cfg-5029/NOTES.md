## Traps
- TR-ABSENT: no block in the settings sheet defines `screw_purge_s`. The neighbouring key `barrel_purge_s` is 260 in the works defaults, and a solver that reads the two names as the same setting reports 260 instead of UNKNOWN. The other keys on the sheet resolve normally, so nothing about the question looks unanswerable.

## Reference solution
1. List the workspace: `README.md`, `config/extruder-stack.json` and a note under `docs/`.
2. Read the settings sheet and walk the three blocks in `resolve_order`. `screw_purge_s` is in none of them: the shift push and the line profile do not mention it, and the works defaults carry `barrel_purge_s`, which is a different setting. With no block defining it, the effective value cannot be determined, so the answer is UNKNOWN.

## Why the answer is unique
The README states that a setting takes its value from a block that defines it, and the sheet is the complete set of blocks the controller consults, so a key none of them mentions has no value at all. The decoy 260 is the works default of `barrel_purge_s`, a different key whose name is close but whose value says nothing about the screw purge; reading one key as the other is the mistake the case is built around. The answer is UNKNOWN.
