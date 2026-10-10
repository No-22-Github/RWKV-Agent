## Traps
- None. The trial note names one soak and the settings file carries one soak, so there is nothing for a solver to weigh up.

## Reference solution
1. Read `config/kiln.json`, the file the README points at: `soak_minutes` is 85.
2. Read the glaze trial note: the satin glaze is fired at a soak of 110 minutes. Change `soak_minutes` to 110 and leave `ramp_degrees_per_hour` and `door_open_delay_s` alone. `tools/report_soak.py`, which the harness runs against the finished workspace, then prints 110.

## Why the answer is unique
The file holds exactly one soak and the trial note names exactly one, so the end state the brief describes is `soak_minutes: 110`; the other two keys describe a ramp and a door delay, not a soak, and the note leaves the large kiln's programme untouched rather than giving a second figure. The checker script reads the key back out of the file, so describing the change in the reply instead of making it does not satisfy the brief. The answer is 110.
