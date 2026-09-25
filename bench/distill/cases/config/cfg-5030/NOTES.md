## Traps
- None. `barrel_purge_s` is carried by the works defaults block alone, so the fall-through order never enters into the answer.

## Reference solution
1. List the workspace: `README.md`, `config/extruder-stack.json` and a note under `docs/`.
2. Read the settings sheet and walk the three blocks in `resolve_order`. The shift push and the line profile do not mention `barrel_purge_s`, so the controller falls through to the works defaults, which carry `barrel_purge_s: 245`.

## Why the answer is unique
Only one block on the sheet defines the barrel purge, so there is no block to weigh it against and no order to apply: the three blocks are the complete set the controller consults, and the shift push and the line profile each set other keys instead. The neighbouring keys in the works defaults (`barrel_heat_c`, `screw_speed_rpm`, `haul_off_gap_mm`) are temperatures, a speed and a gap, so none of them can be read as a purge time. The answer is 245.
