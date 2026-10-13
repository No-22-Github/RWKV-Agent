## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-17, row 2) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "南京", "days": 3} -> 多云
2. web_search 中山陵
Final answer: 中山陵每周一闭馆；南京明天多云。

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. 中山陵哪天闭馆，南京明天天气
2. 明天去中山陵开不开门，天气如何
3. 南京明天天气和中山陵开放时间
4. 查中山陵闭馆日，再看南京明天天气
5. 中山陵周几不开？南京明天下雨吗
