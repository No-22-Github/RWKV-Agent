## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-19, row 4) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "Vancouver", "days": 4} -> 60%
2. web_search capilano
Final answer: Adult admission is CA$72.95; Vancouver on Saturday has a 60% chance of rain.

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. Capilano adult ticket price and Saturday rain chance
2. How much is Capilano, and will it rain Saturday?
3. Vancouver Saturday forecast plus Capilano admission
4. Capilano bridge price; Vancouver weather on the 19th
5. Saturday at Capilano: cost and rain?
