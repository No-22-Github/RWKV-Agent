## Traps
- TR-ABSENT: the fixture has no report for Hallstatt (only Vienna); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were Hallstatt.
- This path keeps an unrecovered `location not found`; `corpus paths` drops such paths today (see b14-authoring.md).

## Reference solution
1. get_weather {"location": "Hallstatt", "days": 3} -> location not found
Final answer: I couldn't find a forecast for Hallstatt (the weather service doesn't know that place).

## Why the answer is unique
The fixture fixes which names resolve; Hallstatt is not one of them.

## Five alternative phrasings of the task
1. Hallstatt天气
2. Hallstatt明天会下雨吗
3. 去Hallstatt要带什么衣服
4. Hallstatt最近天气怎么样
5. Weather in Hallstatt?
