## Traps
- TR-ABSENT: the fixture has no report for 元阳 (only 昆明); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were 元阳.
- Asking for 元阳 first and 昆明 second gives miss-then-success, which `corpus paths` keeps; the other order is dropped.

## Reference solution
1. get_weather {"location": "元阳", "days": 3} -> location not found
2. get_weather {"location": "昆明", "days": 3}
Final answer: 查不到元阳的天气预报（天气服务里没有这个地点）；昆明的情况见上。

## Why the answer is unique
The fixture fixes which names resolve; 元阳 is not one of them.

## Five alternative phrasings of the task
1. 元阳天气
2. 元阳明天会下雨吗
3. 去元阳要带什么衣服
4. 元阳最近天气怎么样
5. Weather in 元阳?
