## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather (今天 is the first row) and 福州地铁 1 号线 运营时间 末班车 from web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 多云: tomorrow is 多云; today (2026-09-16) is 中雨.

## Reference solution
1. get_weather {"location": "福州", "days": 1}
2. web_search 福州地铁 1 号线 运营时间 末班车
Final answer: 福州地铁 1 号线末班车 22:45（首班 6:30）；福州今天有中雨，降水概率 80%，25~28°C，晚上回家带伞。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (22:45).

## Five alternative phrasings of the task
1. 福州地铁 1 号线末班车几点，福州今天天气怎样
2. 今天福州下雨吗？地铁 1 号线最晚几点
3. 福州今天的天气，还有地铁 1 号线运营到几点
4. 查一下福州地铁 1 号线的末班时间和福州今天的天气
5. 福州 1 号线晚上最后一班是几点，今天要带伞吗
