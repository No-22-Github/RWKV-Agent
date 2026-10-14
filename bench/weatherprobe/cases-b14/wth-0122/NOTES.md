## Traps
- TR-ABSENT: the fixture has no report for 涠洲岛 (only 北海); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were 涠洲岛.
- This path keeps an unrecovered `location not found`; `corpus paths` drops such paths today (see b14-authoring.md).

## Reference solution
1. get_weather {"location": "涠洲岛", "days": 3} -> location not found
2. get_weather {"location": "北海", "days": 3}
Final answer: 查不到涠洲岛的天气预报（天气服务里没有这个地点）；北海的情况见上。

## Why the answer is unique
The fixture fixes which names resolve; 涠洲岛 is not one of them.

## Five alternative phrasings of the task
1. 涠洲岛天气
2. 涠洲岛明天会下雨吗
3. 去涠洲岛要带什么衣服
4. 涠洲岛最近天气怎么样
5. Weather in 涠洲岛?
