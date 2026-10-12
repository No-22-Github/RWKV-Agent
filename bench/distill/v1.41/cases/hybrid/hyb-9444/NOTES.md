## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and 厦门 鼓浪屿 轮渡 往返 船票 from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 晴: today is 晴; only tomorrow (2026-09-17) is 阵雨.

## Reference solution
1. get_weather {"location": "厦门", "days": 2}
2. web_search 厦门 鼓浪屿 轮渡 往返 船票
Final answer: 厦门到鼓浪屿的游客往返船票 35 元；厦门明天（9 月 17 日）有阵雨，降水概率 60%，26~31°C，上岛带把伞。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (35).

## Five alternative phrasings of the task
1. 去鼓浪屿的轮渡往返多少钱，厦门明天天气呢
2. 明天上鼓浪屿，船票多少，会下雨吗
3. 厦门明天的天气，还有去鼓浪屿的往返船票
4. 查下鼓浪屿轮渡往返票价，顺便看厦门明天天气
5. 鼓浪屿往返船票多少钱？厦门明天有雨吗
