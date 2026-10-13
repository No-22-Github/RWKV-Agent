## Traps
- TR-ABSENT: the fixture has no report for 喀纳斯 (only 乌鲁木齐); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were 喀纳斯.
- This path keeps an unrecovered `location not found`; `corpus paths` drops such paths today (see b14-authoring.md).

## Reference solution
1. get_weather {"location": "喀纳斯", "days": 3} -> location not found
2. get_weather {"location": "乌鲁木齐", "days": 3}
Final answer: 查不到喀纳斯的天气预报（天气服务里没有这个地点）；乌鲁木齐的情况见上。

## Why the answer is unique
The fixture fixes which names resolve; 喀纳斯 is not one of them.

## Five alternative phrasings of the task
1. 喀纳斯天气
2. 喀纳斯明天会下雨吗
3. 去喀纳斯要带什么衣服
4. 喀纳斯最近天气怎么样
5. Weather in 喀纳斯?
