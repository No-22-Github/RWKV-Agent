## Traps
- TR-DECOY: turn 2: Monday is 2026-09-21 (row 6); a 3-day lookup does not reach it.

## Reference solution
Turn 1:. get_weather {"location": "Melbourne", "days": 3} -> 35%
Turn 2:. get_weather {"location": "Melbourne", "days": 6} -> 60%
Final answer: Melbourne on Monday 21 September: 60% chance of rain.

## Why the answer is unique
The fixed clock (2026-09-16 Wed) maps the day words to one forecast row; the fixture holds one report per city.

## Five alternative phrasings of the task
1. Melbourne rain Monday
2. Will it rain in Melbourne on the 21st?
3. Monday forecast Melbourne
4. Melbourne next Monday weather
5. Is Monday wet in Melbourne?
