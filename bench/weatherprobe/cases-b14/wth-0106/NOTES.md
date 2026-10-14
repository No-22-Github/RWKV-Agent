## Traps
- TR-RULEFILE: the threshold is in events/venue-rules.md

## Reference solution
1. get_weather {"location": "Barcelona", "days": 3} -> 20%
Final answer: Yes: Barcelona tomorrow is partly cloudy with a 20% chance of rain, under the 40% limit.

## Why the answer is unique
The fixed clock (2026-09-16 Wed) maps the day words to one forecast row; the fixture holds one report per city.

## Five alternative phrasings of the task
1. Rooftop dinner Barcelona tomorrow OK?
2. Barcelona rain chance tomorrow
3. Check tomorrow against the venue rules
4. Can we eat outside in Barcelona tomorrow?
5. Venue rule check for Thursday
