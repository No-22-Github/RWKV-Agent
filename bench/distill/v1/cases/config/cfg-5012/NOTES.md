## Traps
- None. `spindle_rpm` is written down once, in `config/cell.yaml`, and no other file in the workspace carries a competing figure.

## Reference solution
1. List the workspace: `README.md`, `config/cell.yaml` and one note under `docs/`.
2. Read `config/cell.yaml`, the file the README names as the cell's only source: `spindle_rpm: 17400`, so the cell runs at 17400 revolutions per minute.

## Why the answer is unique
The speed appears in exactly one place. The README states that the cell takes every value it runs with from that file and that nothing else feeds it, and the other two keys in the file (`feed_rate_mm_min`, `tool_change_s`) describe different limits, so there is no second figure a solver could read as the spindle speed. The answer is 17400.
