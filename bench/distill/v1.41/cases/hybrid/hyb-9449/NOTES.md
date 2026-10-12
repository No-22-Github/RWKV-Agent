## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and Space Needle adult general admission price from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: Sunny: today is Sunny; only tomorrow (2026-09-17) is Drizzle.

## Reference solution
1. get_weather {"location": "Seattle", "days": 2}
2. web_search Space Needle adult general admission price
Final answer: An adult ticket for the Space Needle is $41. Seattle tomorrow (2026-09-17) will have drizzle, 60% chance of rain, 12-18°C, so bring a light rain jacket.

## Why the answer is unique
One forecast row and one web snippet each carry the unique value ($41).

## Five alternative phrasings of the task
1. Space Needle adult ticket price, and Seattle's forecast for tomorrow
2. How much to go up the Space Needle, and will it rain in Seattle tomorrow?
3. Seattle tomorrow: the weather, and the adult Space Needle admission
4. What does the Space Needle cost for an adult, and how's the Seattle weather tomorrow?
5. Before I go up the Space Needle tomorrow: ticket price and Seattle forecast?
