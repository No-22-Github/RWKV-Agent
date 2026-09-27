## Traps
- TR-ABSENT: no file defines `compressor_restart_lock_s`. config/defaults.json carries `compressor_cycle_min` 9, a different compressor setting whose name is close, and a solver that reads the two as one setting reports 9 instead of UNKNOWN.

## Reference solution
1. Read README.md: a key that appears in neither settings layer has no value on this depot.
2. Read config/site-overlay.json: the overlay lists `telemetry_interval_s` and `door_open_warn_s` only.
3. Read config/defaults.json: the compressor key there is `compressor_cycle_min`, not the restart lock.
4. Read docs/alarm-notes.md: compressor protection timings live on the site PLC, outside the ColdChain settings. No value exists in the workspace, so the answer is UNKNOWN.

## Why the answer is unique
The README states that a key in neither layer has no value on the depot, and both layers are in the workspace, so a key no block mentions has nothing to report. The decoy 9 is `compressor_cycle_min`, a cycle-length setting on the same machine; it says nothing about the restart lock, and the notes confirm the protection timings are set on the PLC. The answer is UNKNOWN.
