## Traps
- TR-PRECEDENCE: wind_stop_speed_mps is defined in both layers; the instance
  config (12) overrides the platform defaults (15). A solver who reads only
  config/fleet-defaults.json reports 15.

## Reference solution
1. Read config/crane-fleet.json (path given in the prompt): wind_stop_speed_mps
   is 12 there.
2. Read config/fleet-defaults.json: the defaults carry 15 for the same key.
3. Read README.md: the instance config wins on same-name keys, so the effective
   value is 12.

## Why the answer is unique
The README fixes the direction of the override (instance over defaults), and
both files carry the key with different numbers, so exactly one of the two
figures is effective. The decoy 15 is the defaults figure that loses to the
instance value; nothing in the workspace lets 12 and 15 both be effective.
