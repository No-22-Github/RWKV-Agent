## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-18, row 3) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "青岛", "days": 3} -> 27
2. web_search 啤酒节
Final answer: 啤酒节 9 月 20 日闭幕；青岛后天最高 27°C。

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. 青岛啤酒节闭幕时间，后天青岛气温
2. 后天去青岛，啤酒节还开吗，天气如何
3. 青岛啤酒节什么时候结束，后天多少度
4. 查啤酒节闭幕日，再看青岛后天天气
5. 啤酒节哪天结束？青岛后天热吗
