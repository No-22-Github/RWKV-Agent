## Traps
- TR-DECOY: run_pressure_bar appears in two sections (pump 2.4, drip_lines
  1.1); raising the pump section or editing both is the trap.

## Reference solution
1. Read README.md: the drip lines have their own run_pressure_bar under drip_lines, deliberately lower than the pump's.
2. Read config/irrigation.yaml.
3. Change drip_lines' run_pressure_bar from 1.1 to 1.4, leaving the pump section untouched.

## Why the answer is unique
The README assigns run_pressure_bar to two different sections with distinct
roles, and the request names the drip lines, so only the 1.1 value moves. The
line shape is preserved and the pump's 2.4 stays, so the edited file has
exactly one possible content.
