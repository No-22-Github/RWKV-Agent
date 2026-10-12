## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather (tomorrow is the second row) and Nozomi Tokyo Kyoto reserved seat fare from web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: Cloudy: today is Cloudy; only tomorrow (2026-09-17) is Light rain.

## Reference solution
1. get_weather {"location": "Kyoto", "days": 2}
2. web_search Nozomi Tokyo Kyoto reserved seat fare
Final answer: A reserved seat on the Nozomi from Tokyo to Kyoto is 14,720 yen. Kyoto tomorrow (2026-09-17) will see light rain, 70% chance, 20-25°C, so pack an umbrella.

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (14,720).

## Five alternative phrasings of the task
1. How much is a reserved seat on the Nozomi to Kyoto, and what's Kyoto's weather tomorrow?
2. Nozomi fare Tokyo to Kyoto, plus the Kyoto forecast for tomorrow
3. Kyoto tomorrow: weather, and what does the Nozomi ticket from Tokyo cost?
4. Tell me the Nozomi reserved-seat price to Kyoto and whether it will rain in Kyoto tomorrow
5. Before I head to Kyoto tomorrow: Nozomi reserved fare and the Kyoto forecast?
