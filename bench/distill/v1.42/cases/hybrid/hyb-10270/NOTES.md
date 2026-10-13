## Traps
- TR-ABSENT: the fixture has no report for 霞浦 (only 福州); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were 霞浦.
- This path keeps an unrecovered `location not found`; `corpus paths` drops such paths today (see b14-authoring.md).

## Reference solution
1. get_weather {"location": "霞浦", "days": 3} -> location not found
Final answer: 查不到霞浦的天气预报（天气服务里没有这个地点）；福州的情况见上。

## Why the answer is unique
The fixture fixes which names resolve; 霞浦 is not one of them.

## Five alternative phrasings of the task
1. 霞浦天气
2. 霞浦明天会下雨吗
3. 去霞浦要带什么衣服
4. 霞浦最近天气怎么样
5. Weather in 霞浦?
