## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and 海口东 三亚 环岛高铁 二等座 票价 from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 阵雨: tomorrow is 阵雨; only 后天 (2026-09-18) is 大雨.

## Reference solution
1. get_weather {"location": "海口", "days": 3}
2. web_search 海口东 三亚 环岛高铁 二等座 票价
Final answer: 海口东到三亚环岛高铁二等座 79.5 元；海口后天（9 月 18 日）有大雨，降水概率 85%，26~30°C，出发前备好雨具。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (79.5).

## Five alternative phrasings of the task
1. 环岛高铁海口到三亚二等座多少钱，海口后天天气呢
2. 后天海口去三亚的高铁票价，还有海口那天的天气
3. 海口后天的天气，以及高铁到三亚二等座价格
4. 查下海口东到三亚的二等座票价，再看海口后天天气
5. 海口到三亚二等座要多少？后天海口下大雨吗
