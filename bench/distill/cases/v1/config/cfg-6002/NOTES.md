## Traps
- TR-ABSENT: no file defines `compressor_restart_lock_s`. config/defaults.json carries `compressor_cycle_min` 9, a different compressor setting whose name is close, and a solver that reads the two as one setting reports 9 instead of UNKNOWN.

## Reference solution
1. Read README.md: a key that appears in neither settings layer has no value on this depot.
2. Read config/site-overlay.json: the overlay lists `telemetry_interval_s` and `door_open_warn_s` only.
3. Read config/defaults.json: the compressor key there is `compressor_cycle_min`, not the restart lock.
4. Read docs/alarm-notes.md: compressor protection timings live on the site PLC, outside the ColdChain settings. No file defines `compressor_restart_lock_s`, so no lock duration exists in the workspace.
5. Final answer in two or three sentences: name the files checked, say neither settings layer defines `compressor_restart_lock_s`, and point to `compressor_cycle_min` as a different key without quoting its value. Reference wording: "I checked README.md, config/defaults.json and config/site-overlay.json: the overlay carries telemetry and door-warning keys only, and no layer defines a compressor restart lock. The nearest key is compressor_cycle_min, which is a different compressor setting, so I can't give a lock duration for Marldon." Scored with output_contains_any over "compressor_restart_lock_s", "compressor restart lock" or "restart lock"; output_excludes rules out UNKNOWN and the `compressor_cycle_min` figure, so the reply names the missing key instead of quoting any figure.

## Why the answer is unique
The README states that a key in neither layer has no value on the depot, and both layers are in the workspace, so a key no block mentions has nothing to report. The decoy is `compressor_cycle_min`, a cycle-length setting on the same machine; it says nothing about the restart lock, and the notes confirm the protection timings are set on the PLC. Every accepted surface form — the exact key `compressor_restart_lock_s`, the underscore-free "compressor restart lock", and the shorter "restart lock" — names that one missing key, so each way of scoring points at the same absence, and no wording that reports it can carry a number.
