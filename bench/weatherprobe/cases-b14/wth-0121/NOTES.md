## Traps
- TR-ABSENT: the fixture has no report for 稻城亚丁 (only 成都); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were 稻城亚丁.
- Asking for 稻城亚丁 first and 成都 second gives miss-then-success, which `corpus paths` keeps; the other order is dropped.

## Reference solution
1. get_weather {"location": "稻城亚丁", "days": 3} -> location not found
2. get_weather {"location": "成都", "days": 3}
Final answer: 查不到稻城亚丁的天气预报（天气服务里没有这个地点）；成都的情况见上。

## Why the answer is unique
The fixture fixes which names resolve; 稻城亚丁 is not one of them.

## Five alternative phrasings of the task
1. 稻城亚丁天气
2. 稻城亚丁明天会下雨吗
3. 去稻城亚丁要带什么衣服
4. 稻城亚丁最近天气怎么样
5. Weather in 稻城亚丁?
