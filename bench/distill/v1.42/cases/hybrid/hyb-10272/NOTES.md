## Traps
- TR-ABSENT: the fixture has no report for Tórshavn (only Copenhagen); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were Tórshavn.
- Asking for Tórshavn first and Copenhagen second gives miss-then-success, which `corpus paths` keeps; the other order is dropped.

## Reference solution
1. get_weather {"location": "Tórshavn", "days": 3} -> location not found
2. get_weather {"location": "Copenhagen", "days": 3}
Final answer: I couldn't find a forecast for Tórshavn (the weather service doesn't know that place).

## Why the answer is unique
The fixture fixes which names resolve; Tórshavn is not one of them.

## Five alternative phrasings of the task
1. Tórshavn天气
2. Tórshavn明天会下雨吗
3. 去Tórshavn要带什么衣服
4. Tórshavn最近天气怎么样
5. Weather in Tórshavn?
