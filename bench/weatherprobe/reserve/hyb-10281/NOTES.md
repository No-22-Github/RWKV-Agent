## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (2026-09-17, row 2) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "大连", "days": 3} -> 15%
2. web_search 圣亚
Final answer: 圣亚成人通票 230 元；大连明天降水概率 15%。

## Why the answer is unique
One forecast row and one snippet carry the values.

## Five alternative phrasings of the task
1. 圣亚海洋世界门票，大连明天会下雨吗
2. 明天去圣亚，票价和天气
3. 大连明天天气和圣亚票价
4. 查圣亚成人票，再看大连明天降水
5. 圣亚多少钱？大连明天下雨吗
