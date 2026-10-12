## Traps
- TR-NEARNAME: 漓江 is a scenic spot / district of 桂林, not a city of its own; get_weather resolves cities only, so asking for 漓江 returns location not found and the retry is 桂林 (asking for 桂林 straight away is equally good).
- TR-DECOY: 阴: tomorrow is 阴 with 40%; today (2026-09-16) is 小雨 with 75%.

## Reference solution
1. get_weather {"location": "桂林", "days": 3} (or 漓江 first, then 桂林 after the not-found error; the same failing name is never retried)
Final answer: 漓江在桂林，桂林今天有小雨，降水概率 75%，气温 22~27°C，竹筏游记得带伞或穿雨衣。

## Why the answer is unique
漓江 is a river at 桂林; today is the first forecast row.

## Five alternative phrasings of the task
1. 漓江今天天气如何
2. 今天去漓江漂流会下雨吗
3. 漓江今日天气，要带伞吗
4. 今天漓江竹筏能坐吗，天气怎样
5. Is it raining at the Li River (漓江) today?
