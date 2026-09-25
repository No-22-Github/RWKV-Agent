## Traps
- None. The setting is named in the question, the file holds one value for it, and the README states which unit that value is in.

## Reference solution
1. List the workspace: `README.md`, `config/dispatch-relay.yaml` and one note under `docs/`.
2. Read `config/dispatch-relay.yaml`: `keepalive_window_ms: 95000`, and the README says the window is held in milliseconds. Expressing 95000 milliseconds in seconds gives 95.

## Why the answer is unique
Only one key in the file carries the keep-alive window, and the two neighbouring keys are a different setting measured another way, so the value to read is not in question. 95000 milliseconds is 95 seconds, and the unit the form asks for is fixed by the question. The answer is 95.
