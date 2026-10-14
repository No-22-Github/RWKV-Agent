## Traps
- TR-NEARNAME: 西湖 and 漓江 are sights, not cities; get_weather resolves 杭州 and 桂林. 周六 = 2026-09-19 is the 4th row for 桂林 (days must be >= 4).
- TR-DECOY: 桂林 on Sunday is 25~32 and on 后天 30; Saturday's high is 34.

## Reference solution
Turn 1: get_weather for the first place, answer. Turn 2: get_weather for the new place (a second lookup is needed), answer.
Final answers: 杭州后天（9 月 18 日）降水概率 35%；桂林周六（9 月 19 日）晴，最高 34°C。

## Why the answer is unique
Landmarks map to their cities (杭州, 桂林) and the fixed clock fixes the days.

## Five alternative phrasings of the task
1. 后天去西湖会下雨吗？周六漓江天气怎样、最高几度？
2. 西湖后天降水概率，以及漓江周六的最高气温
3. 后天杭州的雨，周六桂林的高温
4. 先查后天西湖的天气，再查周六漓江
5. Chance of rain at West Lake the day after tomorrow, then the high on Saturday at the Li River?
