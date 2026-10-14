## Traps
- TR-NOTOOLNEED: turn 1 is a concept question (no call). Turn 2 asks a real forecast for 广州, so get_weather is now required (row 2, 2026-09-17).

## Reference solution
Turn 1: no tool call.
Turn 2: get_weather {"location": "广州", "days": 3} -> 0%
Final answer turn 2: 广州 2026-09-17: 0%.

## Why the answer is unique
Turn 1 is a definition; turn 2's value is one forecast row.
