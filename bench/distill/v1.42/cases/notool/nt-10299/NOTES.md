## Traps
- TR-NOTOOLNEED: turn 1 is a concept question (no call). Turn 2 asks a real forecast for 南昌, so get_weather is now required (row 3, 2026-09-18).

## Reference solution
Turn 1: no tool call.
Turn 2: get_weather {"location": "南昌", "days": 3} -> 27
Final answer turn 2: 南昌 2026-09-18: 27.

## Why the answer is unique
Turn 1 is a definition; turn 2's value is one forecast row.
