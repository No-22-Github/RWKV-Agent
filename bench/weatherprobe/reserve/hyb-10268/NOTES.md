## Traps
- TR-ABSENT: the fixture has no report for 阿尔山 (only 呼伦贝尔); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were 阿尔山.
- This path keeps an unrecovered `location not found`; `corpus paths` drops such paths today (see b14-authoring.md).

## Reference solution
1. get_weather {"location": "阿尔山", "days": 3} -> location not found
Final answer: 查不到阿尔山的天气预报（天气服务里没有这个地点）；呼伦贝尔的情况见上。

## Why the answer is unique
The fixture fixes which names resolve; 阿尔山 is not one of them.

## Five alternative phrasings of the task
1. 阿尔山天气
2. 阿尔山明天会下雨吗
3. 去阿尔山要带什么衣服
4. 阿尔山最近天气怎么样
5. Weather in 阿尔山?
