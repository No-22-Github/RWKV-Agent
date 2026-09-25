## Traps
- TR-PRECEDENCE: `dose_window_min` is set in two blocks — 40 in the factory defaults and 22 in the site profile — and the README puts the site profile ahead of the factory defaults, so a solver that takes the value the defaults carry reports 40.

## Reference solution
1. List the workspace: `README.md`, `config/dosing-settings.json` and a note under `docs/`.
2. Read the settings sheet: `resolve_order` lists the historian push, then the site profile, then the factory defaults, and the README states that the first block defining a setting gives it its value. `dose_window_min` is 22 in the site profile and 40 in the factory defaults, so the site profile wins: 22.

## Why the answer is unique
The decoy 40 is the factory default, but the factory defaults are the last block the controller consults; the site profile comes before it in `resolve_order` and defines the setting, so the default never applies. The key also appears in no other file, and the neighbouring keys in the two blocks (`settle_window_min`, `contact_hold_s`, `pump_stroke_percent`) are different settings, so exactly one figure is the dose window. The answer is 22.
