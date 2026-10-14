## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and 龙门石窟 旺季 成人 门票 from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 多云: today is 多云; only tomorrow (2026-09-17) is 雷阵雨.

## Reference solution
1. get_weather {"location": "洛阳", "days": 2}
2. web_search 龙门石窟 旺季 成人 门票
Final answer: 龙门石窟当前旺季成人门票 90 元；洛阳明天（9 月 17 日）有雷阵雨，降水概率 65%，18~26°C，带好雨具。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (90).

## Five alternative phrasings of the task
1. 龙门石窟现在门票多少，洛阳明天天气如何
2. 明天去龙门石窟，票价多少，会下雨吗
3. 洛阳明天的天气，还有龙门石窟门票
4. 查查龙门石窟旺季门票价格，再看洛阳明天天气
5. 龙门石窟成人票多少钱？洛阳明天有雷雨吗
