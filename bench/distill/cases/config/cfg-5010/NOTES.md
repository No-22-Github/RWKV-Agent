## Traps
- None. `posting_batch_lines` is written in one block only, so there is no second value for a solver to weigh against it.

## Reference solution
1. List the workspace: `README.md`, `config/ledger-settings.json` and one note under `docs/`.
2. Read the settings sheet and walk the three blocks in `resolved_from`. Only the shipped defaults define `posting_batch_lines`, with 480, and no earlier source carries the key, so the effective value is 480.

## Why the answer is unique
The README fixes how a setting gets its value, and exactly one block in the sheet defines this one, so no other figure is a defensible reading: 110 and 75 belong to `reconcile_window_min` in other blocks, and 495 to the retention setting. The neighbouring keys describe different limits of the service. The answer is 480.
