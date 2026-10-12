## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather (明天 is the second row) and 苏州博物馆 开放时间 停止入馆 from web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 阴: today is 阴; only tomorrow (2026-09-17) is 阵雨. The page also lists 17:00 as the closing time, which is not the cut-off.

## Reference solution
1. get_weather {"location": "苏州", "days": 2}
2. web_search 苏州博物馆 开放时间 停止入馆
Final answer: 苏州博物馆 16:00 停止入馆（17:00 闭馆，周一闭馆）；苏州明天（9 月 17 日）有阵雨，降水概率 55%，24~28°C，带把伞。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (16:00).

## Five alternative phrasings of the task
1. 苏州博物馆下午几点停止入馆，苏州明天天气怎样
2. 明天去苏州博物馆，最晚几点进，苏州会下雨吗
3. 苏州明天的天气，还有博物馆的停止入馆时间
4. 查查苏州博物馆的开放时间，再看苏州明天天气
5. 苏州博物馆几点不让进了？明天苏州天气呢
