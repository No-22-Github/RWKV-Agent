## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-18, row 3) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "Lisbon", "days": 3} -> 5%
2. web_search tram 28
Final answer: A single tram ticket bought on board is €3.10.

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. Tram 28 single fare on board
2. How much is a Lisbon tram ticket?
3. Carris tram ticket price
4. Cost of riding tram 28 once
5. On-board tram fare in Lisbon
