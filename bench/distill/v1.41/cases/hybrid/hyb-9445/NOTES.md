## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and Heathrow Express adult single fare Paddington from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: Overcast: today is Overcast; only tomorrow (2026-09-17) is Light rain.

## Reference solution
1. get_weather {"location": "London", "days": 2}
2. web_search Heathrow Express adult single fare Paddington
Final answer: An adult single on the Heathrow Express to Paddington is £25 booked online (15 minutes). London tomorrow (2026-09-17) will see light rain, 75% chance, 11-15°C, so bring an umbrella.

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (£25).

## Five alternative phrasings of the task
1. Heathrow Express adult single fare to Paddington, plus London's forecast for tomorrow
2. How much is the Heathrow Express and will it rain in London tomorrow?
3. London tomorrow: weather, and the price of the Heathrow Express to Paddington
4. What does an adult single on the Heathrow Express cost, and what's tomorrow's London weather?
5. Tomorrow I arrive in London: Heathrow Express fare and the forecast, please
