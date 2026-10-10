## Traps
- None. `queue_capacity` is written down once, in `config/benchsched.yaml`, and no other file in the workspace carries a competing figure.

## Reference solution
1. List the workspace: `README.md`, `config/benchsched.yaml` and one note under `docs/`.
2. Read `config/benchsched.yaml`, the settings file the README names: `queue_capacity: 48`, so the scheduler holds 48 booking requests and turns anything past that away.

## Why the answer is unique
The queue size appears in exactly one place. The README states that the scheduler reads its settings from that file and that nothing is exported into its environment, so there is no second source a solver could consult, and the other two keys in the file (`hold_seconds`, `session_max_minutes`) describe different limits. The answer is 48.
