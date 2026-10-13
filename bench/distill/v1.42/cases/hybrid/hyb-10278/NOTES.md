## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-19, row 4) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "长沙", "days": 4} -> 晴
2. web_search 橘子洲
Final answer: 橘子洲焰火周六 20:30 燃放；长沙周六晴。

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. 橘子洲焰火几点开始，长沙周六天气
2. 周六看焰火，时间和天气
3. 长沙周六会下雨吗，焰火几点
4. 查橘子洲焰火时间，再看长沙周六天气
5. 橘子洲周六焰火几点？那天天气呢
