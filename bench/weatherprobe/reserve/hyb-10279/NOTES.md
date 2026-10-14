## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-17, row 2) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "Osaka", "days": 3} -> Partly cloudy
2. web_search kaiyukan
Final answer: Kaiyukan closes at 20:00 (last entry 19:00); Osaka tomorrow: Partly cloudy.

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. Kaiyukan closing time and Osaka weather tomorrow
2. When does the Osaka aquarium close? Will it rain tomorrow?
3. Osaka tomorrow: aquarium hours and forecast
4. Kaiyukan hours plus tomorrow's weather
5. What time does Kaiyukan shut, and tomorrow's Osaka forecast?
