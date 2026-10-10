## Traps
- None. Only the factory defaults block carries `rinse_cycles`, and the two blocks the controller consults before it leave the setting out, so the value falls through to that one figure with nothing to compare it against.

## Reference solution
1. List the workspace: `README.md`, `config/dosing-settings.json` and a note under `docs/`.
2. Read the settings sheet and walk the three blocks in `resolve_order`: the historian push and the site profile do not mention `rinse_cycles`, and the factory defaults carry `rinse_cycles: 8`, so the controller runs 8 cycles.

## Why the answer is unique
The README states that a setting takes its value from the first block that defines it, and exactly one block defines `rinse_cycles`, so there is no second figure to weigh up. The neighbouring keys in the same block concern other settings, and no other file in the workspace lists controller settings at all. The answer is 8.
