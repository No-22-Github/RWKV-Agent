## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-17, row 2) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "苏州", "days": 3} -> 雷阵雨
2. web_search 拙政园
Final answer: 拙政园旺季门票 90 元。

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. 拙政园门票多少
2. 拙政园旺季票价
3. 苏州拙政园现在多少钱
4. 拙政园成人票价格
5. 去拙政园要买多少钱的票
