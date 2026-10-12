## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather (明天 is the second row) and 北京南 南京南 高铁 二等座 票价 from web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 多云: today is 多云; only tomorrow (2026-09-17) is 小雨.

## Reference solution
1. get_weather {"location": "南京", "days": 2}
2. web_search 北京南 南京南 高铁 二等座 票价
Final answer: 北京南到南京南二等座票价 443.5 元；南京明天（9 月 17 日）有小雨，降水概率 60%，气温 21~26°C，记得带伞。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (443.5).

## Five alternative phrasings of the task
1. 北京南到南京南二等座多少钱，再看南京明天天气
2. 查一下去南京的高铁二等座票价，还有南京明天会不会下雨
3. 南京明天天气如何？北京到南京高铁二等座要多少钱
4. 明天北京去南京的高铁票价和南京的天气
5. 北京南—南京南二等座票价是多少，南京明天什么天气
