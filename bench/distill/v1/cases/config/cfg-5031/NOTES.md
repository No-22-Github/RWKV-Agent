## Traps
- TR-PRECEDENCE: `barrel_heat_c` is defined by all three blocks. The shift push carries 226, the line profile 212 and the works defaults 188. Reading the sheet as a whole rather than in the order the controller consults the blocks gives 212, and reading it bottom-up gives 188.

## Reference solution
1. List the workspace: `README.md`, `config/extruder-stack.json` and a note under `docs/`.
2. Read the settings sheet and walk the three blocks in `resolve_order`. The shift push comes first and carries `barrel_heat_c: 226`, so the controller takes that figure and never reaches the entry in the line profile or the one in the works defaults.

## Why the answer is unique
The README fixes the order of the blocks and says that the first block defining a setting gives it its value, so two later entries for the same key cannot change the figure the controller runs with. The decoy 212 is the line profile entry, which the controller only consults for keys the shift push leaves unset, and 188 is the works default, which is reached only when both blocks above it are silent. The answer is 226.
