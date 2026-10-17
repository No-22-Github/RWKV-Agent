## Traps
TR-ABSENT

## Reference solution
1. get_weather 双廊古镇 -> not found; retry with 大理 / 洱海 -> not found (fixture only holds 昆明).
Final answer must say the forecast cannot be found, not invent one.

## Why the answer is unique
Recomputed from the fixture / fixed clock (2026-09-16 10:00 Asia/Shanghai). Expected: ["any", ["查不到", "找不到", "没有找到", "未找到", "无法查询", "无法获取", "没有查到", "没查到", "不支持", "not found", "couldn't find", "could not find", "unable", "no data"]] 

## Five alternative phrasings of the task
1. 双廊古镇明天天气
2. 洱海双廊明天会下雨吗
3. 查一下双廊的天气预报
4. 大理双廊古镇明天天气如何
5. Weather at Shuanglang town tomorrow?
