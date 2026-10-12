## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and 广州塔 成人 观光票 价格 from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 多云: tomorrow is 多云; today (2026-09-16) is 雷阵雨.

## Reference solution
1. get_weather {"location": "广州", "days": 1}
2. web_search 广州塔 成人 观光票 价格
Final answer: 广州塔主塔观光票成人 150 元；广州今天有雷阵雨，降水概率 75%，26~32°C，晚上出门带好伞。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (150).

## Five alternative phrasings of the task
1. 广州塔成人票多少钱，广州今天天气如何
2. 今天去广州塔，票价多少，会下雨吗
3. 广州今天的天气，还有广州塔观光票价格
4. 查下广州塔成人票价，再看广州今天天气
5. 广州塔观光票要多少？今天广州有雷雨吗
