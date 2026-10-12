## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and 成都 大熊猫基地 入园时间 from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 多云: today is 多云; only tomorrow (2026-09-17) is 小雨. The page also lists 18:00 as the ticket cut-off, which is not the opening time.

## Reference solution
1. get_weather {"location": "成都", "days": 2}
2. web_search 成都 大熊猫基地 入园时间
Final answer: 成都大熊猫基地 7:30 开始入园；成都明天（9 月 17 日）有小雨，降水概率 70%，气温 20~25°C，记得带伞。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (7:30).

## Five alternative phrasings of the task
1. 成都熊猫基地几点开门，成都明天天气怎样
2. 明天去看熊猫，基地几点入园，会下雨吗
3. 成都明天的天气，还有熊猫基地的入园时间
4. 查一下成都大熊猫基地的入园时间，再看明天成都天气
5. 熊猫基地早上几点能进？成都明天要带伞吗
