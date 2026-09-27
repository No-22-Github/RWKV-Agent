## Traps
- TR-ABSENT: neither file defines `pallet_wrap_tension_n`. config/orchard-base.json carries `case_tape_tension_n` 18, a tension setting with a close name, and a solver that reads the two as one setting reports 18 instead of UNKNOWN.

## Reference solution
1. Read README.md: the controller reads the base file, the profile replaces what it sets, and anything else is fixed in the firmware.
2. Read config/orchard-base.json: it holds crate, belt, label, seal and case-tape keys, and `case_tape_tension_n` is tape on the crates, not film on the pallets.
3. Read profiles/packing-line.ini: it sets crate weight and label delay only.
4. Read docs/line-notes.md: nothing there carries the shrink-wrap station's settings. No value exists, so the answer is UNKNOWN.

## Why the answer is unique
Both settings files are in the workspace and neither lists `pallet_wrap_tension_n`, and the README states that whatever the two files do not carry is fixed in the firmware, so no effective value can be read off the workspace. The decoy 18 belongs to `case_tape_tension_n`, a different tension on a different material, so reading one as the other is the mistake the case is built around. The answer is UNKNOWN.
