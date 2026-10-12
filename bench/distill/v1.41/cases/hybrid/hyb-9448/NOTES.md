## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and 内蒙古博物院 开放时间 闭馆 from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: 多云: tomorrow is 多云; only 后天 (2026-09-18) is 阵雨. The page also lists opening hours, which are not the closing day.

## Reference solution
1. get_weather {"location": "呼和浩特", "days": 3}
2. web_search 内蒙古博物院 开放时间 闭馆
Final answer: 内蒙古博物院每周一闭馆（开放时间 9:00—17:00）；呼和浩特后天（9 月 18 日，周五）有阵雨，降水概率 55%，8~17°C，偏凉，带伞加外套。

## Why the answer is unique
One forecast row and one web snippet each carry the unique value (周一).

## Five alternative phrasings of the task
1. 内蒙古博物院每周几闭馆，呼和浩特后天天气呢
2. 后天去内蒙古博物院，哪天不开门，那天天气如何
3. 呼和浩特后天的天气，还有内蒙古博物院的闭馆日
4. 查一下内蒙古博物院哪天闭馆，再看呼和浩特后天天气
5. 内蒙古博物院周几休息？呼和浩特后天会下雨吗
