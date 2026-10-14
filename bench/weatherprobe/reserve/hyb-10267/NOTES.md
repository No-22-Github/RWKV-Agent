## Traps
- TR-ABSENT: the fixture has no report for 婺源 (only 南昌); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were 婺源.
- This path keeps an unrecovered `location not found`; `corpus paths` drops such paths today (see b14-authoring.md).

## Reference solution
1. get_weather {"location": "婺源", "days": 3} -> location not found
Final answer: 查不到婺源的天气预报（天气服务里没有这个地点）；南昌的情况见上。

## Why the answer is unique
The fixture fixes which names resolve; 婺源 is not one of them.

## Five alternative phrasings of the task
1. 婺源天气
2. 婺源明天会下雨吗
3. 去婺源要带什么衣服
4. 婺源最近天气怎么样
5. Weather in 婺源?
