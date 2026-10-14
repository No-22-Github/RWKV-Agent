## Traps
- TR-PRECEDENCE: config/defaults.json carries `telemetry_interval_s` 90 and config/site-overlay.json re-sets it to 45. A solver that reads the defaults first and stops, or that resolves the two layers in the wrong order, reports 90.

## Reference solution
1. Read README.md: the depot's settings resolve in two layers, and a key the site overlay lists replaces the shipped default.
2. Read config/site-overlay.json: `telemetry_interval_s` is listed there with 45.
3. Read config/defaults.json: 90 is the shipped default that the overlay replaces. The effective value is 45.

## Why the answer is unique
The README fixes the direction of resolution: the overlay replaces the default, and the overlay is the only place a Marldon value is written. The decoy 90 is the shipped default, which applies only to depots that do not list the key in their overlay, so reading it as Marldon's effective value is the mistake the case is built around. The answer is 45.
