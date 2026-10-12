## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather (明天 is the second row) and 日元 人民币 中间价 from web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 晴: today is 晴; only tomorrow (2026-09-17) is 雷阵雨.

## Reference solution
1. get_weather {"location": "东京", "days": 2}
2. web_search 日元 人民币 中间价
Final answer: 今天中间价 100 日元 = 4.52 元人民币；东京明天（9 月 17 日）有雷阵雨，降水概率 65%，22~28°C，出门带伞。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (4.52).

## Five alternative phrasings of the task
1. 100 日元现在换多少人民币，东京明天天气如何
2. 查下日元兑人民币的中间价，再看东京明天的天气
3. 东京明天会下雨吗？100 日元折合人民币多少
4. 去东京之前想知道日元汇率，还有东京明天天气
5. 今天 100 日元兑人民币中间价多少，明天东京天气呢
